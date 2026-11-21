import java.io.*;
import java.nio.*;
import java.nio.channels.FileChannel;
import java.nio.file.*;
import java.util.*;

import net.minecraft.SharedConstants;
import net.minecraft.nbt.*;
import net.minecraft.server.Bootstrap;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.chunk.storage.RegionFileStorage;
import net.minecraft.world.level.chunk.storage.RegionStorageInfo;

/**
 * T-022 terrain backend for big areas (server STOPPED), chunk by chunk.
 *   Terrain scan  <world> <x1> <z1> <x2> <z2> <out.bin>   per column: ground (trees, plants, water ignored), top (first non-air), water top, flags
 *   (flowing water counts as air: it spreads while chunks tick, differently on every build from scratch)
 *   Terrain apply <world> <grid.bin>                      rewrites the columns of the grid that have a height (others untouched)
 * scan file: "LETS" + int x0 z0 w h, then int16 ground[w*h], int16 top[w*h], int16 water[w*h], uint8 flags[w*h]
 *   (index (z-z0)*w + (x-x0); -32768 = none / chunk missing; flags 1 log above ground, 2 leaves, 4 water, 8 lava, 16 chunk missing)
 * grid file: "LETA" + int x0 z0 w h, then int16 H[w*h] (-32768 = keep), int16 floor[w*h] (columns are rewritten from floor up),
 *   int16 water[w*h] (water fill H+1..water; -32768 none), uint8 surf[w*h], uint8 rock[w*h], uint8 aux[w*h]
 * Columns are rewritten from floor to the build limit: rock style below, surface style on top, air above (or water). Only the touched
 * columns lose block entities, block ticks and entities (from floor up): what stands next to them stays. Light and heightmaps are
 * dropped for touched chunks, the server rebuilds them.
 */
public class Terrain {
    static final int MINY = -64, MAXY = 319, NONE = -32768;
    static final Map<String, Tag> TAGS = new HashMap<>();
    static Tag T(String n) { return TAGS.computeIfAbsent(n, k -> {
        if (!k.contains("[")) return StringTag.valueOf("minecraft:" + k);
        String id = k.substring(0, k.indexOf('[')); CompoundTag c = new CompoundTag(); c.putString("id", "minecraft:" + id); CompoundTag p = new CompoundTag();
        for (String kv : k.substring(k.indexOf('[') + 1, k.length() - 1).split(",")) { String[] a = kv.split("="); p.putString(a[0], a[1]); }
        c.put("properties", p); return c; }); }
    static String nameOf(Tag t) {
        if (t instanceof StringTag s) return s.value().replace("minecraft:", "");
        CompoundTag c = (CompoundTag) t; return c.getString("id").orElseGet(() -> c.getStringOr("", "minecraft:air")).replace("minecraft:", "");
    }
    static final Tag AIR = StringTag.valueOf("minecraft:air");
    /** flowing water (level 1..15): it spreads while the pregenerated chunks tick, so two builds from scratch see it differently
     *  (review T-025, point 6); the scan counts it as air */
    static boolean flowing(Tag t) {
        if (!(t instanceof CompoundTag c)) return false;
        String lv = c.getCompound("properties").map(p -> p.getStringOr("level", "0")).orElse("0");
        return !lv.equals("0");
    }

    static Tag[] decode(CompoundTag sec) {
        Tag[] out = new Tag[4096]; CompoundTag bs = sec.getCompoundOrEmpty("block_states"); ListTag pal = bs.getListOrEmpty("palette");
        if (pal.isEmpty()) { Arrays.fill(out, AIR); return out; }
        long[] data = bs.getLongArray("data").orElse(null);
        if (data == null || pal.size() == 1) { Arrays.fill(out, pal.get(0)); return out; }
        int bits = Math.max(4, 32 - Integer.numberOfLeadingZeros(pal.size() - 1)), per = 64 / bits; long mask = (1L << bits) - 1;
        for (int i = 0; i < 4096; i++) out[i] = pal.get((int) ((data[i / per] >>> ((i % per) * bits)) & mask));
        return out;
    }
    static void encode(CompoundTag sec, Tag[] blocks) {
        LinkedHashMap<String, Integer> pm = new LinkedHashMap<>(); ListTag pal = new ListTag(); int[] idx = new int[4096];
        for (int i = 0; i < 4096; i++) { String k = blocks[i].toString(); Integer p = pm.get(k); if (p == null) { p = pm.size(); pm.put(k, p); pal.add(blocks[i]); } idx[i] = p; }
        CompoundTag bs = new CompoundTag(); bs.put("palette", pal);
        if (pal.size() > 1) { int bits = Math.max(4, 32 - Integer.numberOfLeadingZeros(pal.size() - 1)), per = 64 / bits; long[] d = new long[(4096 + per - 1) / per];
            for (int i = 0; i < 4096; i++) d[i / per] |= ((long) idx[i]) << ((i % per) * bits); bs.put("data", new LongArrayTag(d)); }
        sec.put("block_states", bs); sec.remove("SkyLight"); sec.remove("BlockLight");
    }

    // ---------- classification for scans ----------
    static final Set<String> SKIP = new HashSet<>(Arrays.asList("air", "cave_air", "void_air", "barrier", "water", "lava", "short_grass", "tall_grass", "fern", "large_fern", "snow", "vine",
        "dead_bush", "bush", "leaf_litter", "wildflowers", "sugar_cane", "seagrass", "tall_seagrass", "kelp", "kelp_plant", "sweet_berry_bush", "firefly_bush", "short_dry_grass",
        "tall_dry_grass", "pumpkin", "moss_carpet", "pale_moss_carpet", "pale_hanging_moss", "bamboo", "cactus", "cocoa", "lily_pad", "glow_lichen", "hanging_roots", "red_bush",
        "big_dripleaf", "big_dripleaf_stem", "small_dripleaf", "brown_mushroom_block", "red_mushroom_block", "mushroom_stem", "bee_nest", "creaking_heart", "resin_clump", "pointed_dripstone"));
    static int kind(String n) { // 0 ground, 1 skip (plant/air), 2 log, 3 leaves, 4 water, 5 lava
        if (n.equals("water") || n.equals("bubble_column") || n.equals("ice")) return 4;   // ice: water that froze while the chunks ticked (review T-025, 6)
        if (n.equals("lava")) return 5;
        if (n.endsWith("leaves")) return 3;
        if (n.endsWith("_log") || n.endsWith("_wood") || n.endsWith("_stem") || n.endsWith("_hyphae") || n.contains("mangrove_roots")) return 2;
        if (SKIP.contains(n) || n.contains("flower") || n.contains("tulip") || n.contains("mushroom") || n.endsWith("sapling") || n.equals("poppy") || n.equals("dandelion")
            || n.contains("orchid") || n.contains("allium") || n.contains("bluet") || n.contains("daisy") || n.contains("lily") || n.contains("rose") || n.equals("lilac")
            || n.equals("peony") || n.contains("cornflower") || n.contains("dripleaf") || n.contains("eyeblossom") || n.contains("petals") || n.contains("bush") || n.contains("carpet")) return 1;
        return 0;
    }

    public static void main(String[] a) throws Exception {
        SharedConstants.tryDetectVersion(); Bootstrap.bootStrap();
        switch (a[0]) {
            case "scan" -> scan(Paths.get(a[1]), Integer.parseInt(a[2]), Integer.parseInt(a[3]), Integer.parseInt(a[4]), Integer.parseInt(a[5]), Paths.get(a[6]));
            case "apply" -> apply(Paths.get(a[1]), Paths.get(a[2]));
            default -> throw new IllegalArgumentException(a[0]);
        }
    }
    static RegionFileStorage open(Path world, String kind) throws IOException {
        Path d = world.resolve("dimensions/minecraft/overworld/" + (kind.equals("chunk") ? "region" : kind));
        return new RegionFileStorage(new RegionStorageInfo("world", Level.OVERWORLD, kind), d, false);
    }
    static Tag[][] sections(CompoundTag ch, Map<Integer, Integer> yToIdx) {
        ListTag secs = ch.getListOrEmpty("sections"); Tag[][] out = new Tag[24][];
        for (int i = 0; i < secs.size(); i++) { int y = secs.getCompoundOrEmpty(i).getByteOr("Y", (byte) 0); if (y >= -4 && y < 20) { yToIdx.put(y, i); } }
        for (int s = 0; s < 24; s++) { Integer i = yToIdx.get(s - 4); if (i == null) { out[s] = new Tag[4096]; Arrays.fill(out[s], AIR); } else out[s] = decode(secs.getCompoundOrEmpty(i)); }
        return out;
    }
    static Tag at(Tag[][] b, int lx, int y, int lz) { return b[(y - MINY) >> 4][(((y - MINY) & 15) << 8) | (lz << 4) | lx]; }
    static void put(Tag[][] b, int lx, int y, int lz, Tag t) { b[(y - MINY) >> 4][(((y - MINY) & 15) << 8) | (lz << 4) | lx] = t; }

    static void scan(Path world, int x1, int z1, int x2, int z2, Path out) throws Exception {
        int w = x2 - x1 + 1, h = z2 - z1 + 1, n = w * h; short[] g = new short[n], top = new short[n], wat = new short[n]; byte[] fl = new byte[n];
        Arrays.fill(g, (short) NONE); Arrays.fill(top, (short) NONE); Arrays.fill(wat, (short) NONE);
        long t0 = System.currentTimeMillis(); int missing = 0;
        try (RegionFileStorage st = open(world, "chunk")) {
            for (int cz = Math.floorDiv(z1, 16); cz <= Math.floorDiv(z2, 16); cz++) for (int cx = Math.floorDiv(x1, 16); cx <= Math.floorDiv(x2, 16); cx++) {
                CompoundTag ch = st.read(new ChunkPos(cx, cz));
                boolean full = ch != null && ch.getStringOr("Status", "").endsWith("full");
                Tag[][] b = full ? sections(ch, new HashMap<>()) : null; if (!full) missing++;
                for (int lz = 0; lz < 16; lz++) for (int lx = 0; lx < 16; lx++) {
                    int x = cx * 16 + lx, z = cz * 16 + lz; if (x < x1 || x > x2 || z < z1 || z > z2) continue;
                    int i = (z - z1) * w + (x - x1);
                    if (b == null) { fl[i] = 16; continue; }
                    int f = 0;
                    for (int y = MAXY; y >= MINY; y--) {
                        Tag bt = at(b, lx, y, lz); int k = kind(nameOf(bt));
                        if (k == 4 && flowing(bt)) k = 1;
                        if (k != 1 && top[i] == NONE) top[i] = (short) y;
                        if (k == 4) { if (wat[i] == NONE) wat[i] = (short) y; f |= 4; }
                        else if (k == 5) f |= 8;
                        else if (k == 2) f |= 1;
                        else if (k == 3) f |= 2;
                        else if (k == 0) { g[i] = (short) y; break; }
                    }
                    fl[i] = (byte) f;
                }
            }
        }
        try (DataOutputStream o = new DataOutputStream(new BufferedOutputStream(Files.newOutputStream(out), 1 << 20))) {
            ByteBuffer hd = ByteBuffer.allocate(20).order(ByteOrder.LITTLE_ENDIAN); hd.put("LETS".getBytes()); hd.putInt(x1).putInt(z1).putInt(w).putInt(h); o.write(hd.array());
            ByteBuffer bb = ByteBuffer.allocate(n * 2).order(ByteOrder.LITTLE_ENDIAN);
            for (short[] arr : new short[][]{g, top, wat}) { bb.clear(); for (short s : arr) bb.putShort(s); o.write(bb.array()); }
            o.write(fl);
        }
        System.out.printf("scan: %dx%d columns, %d chunks missing or unfinished, %.1fs -> %s%n", w, h, missing, (System.currentTimeMillis() - t0) / 1000.0, out);
    }

    // ---------- column composition ----------
    static double hash(int x, int y, int z, int salt) {
        long n = x * 374761393L + y * 1442695040888963407L + z * 668265263L + salt * 2654435761L; n = (n ^ (n >>> 13)) * 1274126177L; n ^= n >>> 16;
        return ((n & 0xffffff) / (double) 0x1000000);
    }
    static double vnoise(double x, double z, int salt) {
        int xi = (int) Math.floor(x), zi = (int) Math.floor(z); double fx = x - xi, fz = z - zi;
        fx = fx * fx * (3 - 2 * fx); fz = fz * fz * (3 - 2 * fz);
        double a = hash(xi, 0, zi, salt), b = hash(xi + 1, 0, zi, salt), c = hash(xi, 0, zi + 1, salt), d = hash(xi + 1, 0, zi + 1, salt);
        return (a * (1 - fx) + b * fx) * (1 - fz) + (c * (1 - fx) + d * fx) * fz;
    }
    static Tag pick(int x, int y, int z, int salt, Object... wb) { // weights then names: 40,"stone",20,"tuff"...
        double tot = 0; for (int i = 0; i < wb.length; i += 2) tot += ((Number) wb[i]).doubleValue();
        double r = hash(x, y, z, salt) * tot, acc = 0;
        for (int i = 0; i < wb.length; i += 2) { acc += ((Number) wb[i]).doubleValue(); if (r <= acc) return T((String) wb[i + 1]); }
        return T((String) wb[wb.length - 1]);
    }
    /** rock styles: 0 plain stone, 1 west ridge strata, 2 charred east ridge, 3 rift wall (Dol side, dark), 4 rift wall (south: red clay, sandstone),
     *  5 north ridge (light strata), 6 wall body south half, 7 wall body north half, 8 deepslate dark (rift floor), 9 castle rock (T-028) */
    static Tag rock(int style, int x, int y, int z) {
        double band = (y + vnoise(x / 23.0, z / 23.0, 51) * 7) / 4.0; int b = Math.floorMod((int) Math.floor(band + hash(x / 7, 0, z / 7, 52) * 0.8), 6);
        switch (style) {
            case 1: return switch (b) { case 0, 3 -> T("stone"); case 1 -> T("andesite"); case 2, 5 -> T("tuff"); default -> pick(x, y, z, 3, 3, "stone", 2, "cobblestone", 1, "andesite"); };
            case 2: return switch (b) { case 0, 3 -> T("basalt[axis=y]"); case 1 -> T("blackstone"); case 2 -> T("tuff"); case 4 -> T("smooth_basalt"); default -> pick(x, y, z, 4, 3, "blackstone", 2, "basalt[axis=y]", 1, "tuff"); };
            case 3: return switch (b) { case 0, 3 -> T("deepslate[axis=y]"); case 1 -> T("tuff"); case 2 -> T("cobbled_deepslate"); case 4 -> T("smooth_basalt"); default -> pick(x, y, z, 5, 3, "deepslate[axis=y]", 2, "tuff", 1, "andesite"); };
            case 4: { int bb = Math.floorMod(Math.floorDiv(y, 3), 7);   // horizontal strata (HQ review T-022, 5); same as rift_rock() in r1.py
                return switch (bb) { case 0 -> T("red_terracotta"); case 1 -> T("terracotta"); case 2 -> T("red_sandstone"); case 3 -> T("orange_terracotta"); case 4 -> T("sandstone"); case 5 -> T("brown_terracotta"); default -> T("red_sandstone"); }; }
            case 5: return switch (b) { case 0, 3 -> T("stone"); case 1 -> T("andesite"); case 2 -> T("tuff"); case 4 -> T("calcite"); default -> T("stone"); };
            case 8: return pick(x, y, z, 8, 5, "deepslate[axis=y]", 2, "tuff", 2, "cobbled_deepslate");
            case 9: return pick(x, y, z, 31, 40, "stone", 20, "tuff", 20, "andesite", 10, "cobbled_deepslate", 6, "mossy_cobblestone", 4, "moss_block");   // T-028 castle rock (card palette)
            default: return y < 0 - (int) (hash(x >> 1, 0, z >> 1, 7) * 6) ? T("deepslate[axis=y]") : T("stone");
        }
    }
    /** surface styles (top `depth` blocks): returns null = keep rock */
    static Tag surf(int style, int x, int y, int z, int depth, int H) {
        switch (style) {
            case 1: return depth == 0 ? T("grass_block[snowy=false]") : depth < 4 ? T("dirt") : null;
            case 2: return depth == 0 ? pick(x, y, z, 21, 5, "grass_block[snowy=false]", 3, "podzol[snowy=false]", 2, "coarse_dirt") : depth < 4 ? T("dirt") : null;
            case 3: return depth == 0 ? pick(x, y, z, 22, 4, "coarse_dirt", 3, "podzol[snowy=false]", 2, "grass_block[snowy=false]", 1, "gravel") : depth < 3 ? T("dirt") : null;
            case 4: return depth < 2 ? T("snow_block") : null;
            case 5: return depth == 0 ? pick(x, y, z, 23, 5, "gravel", 3, "coarse_dirt", 2, "sand", 1, "cobblestone") : depth < 3 ? pick(x, y, z, 24, 3, "gravel", 1, "dirt") : null;
            case 6: return depth == 0 ? pick(x, y, z, 25, 6, "moss_block", 4, "grass_block[snowy=false]") : depth < 3 ? T("dirt") : null;
            case 7: return depth == 0 ? pick(x, y, z, 26, 5, "coarse_dirt", 3, "gravel", 2, "stone") : depth < 3 ? T("dirt") : null;   // flat ground of a platform (Black Post)
            case 8: return depth == 0 ? pick(x, y, z, 27, 5, "coarse_dirt", 3, "podzol[snowy=false]", 2, "blackstone", 1, "gravel") : depth < 3 ? T("coarse_dirt") : null;  // charred slope
            case 9: return depth == 0 ? pick(x, y, z, 28, 6, "gravel", 3, "red_sand", 2, "coarse_dirt", 1, "cobblestone") : depth < 2 ? T("gravel") : null;  // dry riverbed
            case 10: return depth == 0 ? pick(x, y, z, 29, 4, "stone", 3, "andesite", 2, "tuff", 1, "cobblestone") : null;  // bare rock top
            case 11: return depth == 0 ? pick(x, y, z, 32, 5, "moss_block", 3, "stone", 1, "andesite", 1, "tuff") : depth == 1 ? pick(x, y, z, 33, 1, "moss_block", 2, "stone") : null;  // T-028 castle rock top: rock with moss
            case 12: return depth == 0 ? pick(x, y, z, 34, 4, "gravel", 3, "mud", 2, "clay", 1, "dirt") : depth < 3 ? pick(x, y, z, 35, 2, "dirt", 1, "clay") : null;  // T-028 lake bed
            default: return null;
        }
    }
    static void column(Tag[] c, int x, int z, int H, int fl, int W, int sf, int rk, int aux) {
        for (int y = fl; y <= MAXY; y++) {
            Tag t;
            if (y > H) t = (W != NONE && y <= W) ? T("water[level=0]") : AIR;
            else if (rk == 6 || rk == 7) t = wall(x, y, z, H, rk == 7, aux);
            else { Tag s = sf > 0 ? surf(sf, x, y, z, H - y, H) : null; t = s != null ? s : rock(rk, x, y, z); }
            c[y - MINY] = t;
        }
        if (sf == 4 && H + 1 <= MAXY && (W == NONE || W <= H)) c[H + 1 - MINY] = T("snow[layers=" + (1 + (int) (hash(x, 0, z, 9) * 2)) + "]");
        if (rk == 6 || rk == 7) { if (H >= 213 && H <= 215 && H + 1 <= MAXY) c[H + 1 - MINY] = T("snow[layers=1]"); }
    }
    /** the Wall (card «Стена», Р3 party 1): aux = distance to the nearest face (0..), north: rk 7. Socle y..100 masonry, ice body 101..212,
     *  dark bands every 12..16 blocks (face layer only), crest 213..215 packed ice under snow, parapets (H >= 216) of deepslate bricks with a wall on top */
    static Tag wall(int x, int y, int z, int H, boolean north, int dist) {
        if (H >= 216 && y >= 213) return y == H ? T("deepslate_brick_wall[east=low,north=none,south=none,up=true,waterlogged=false,west=low]") : T("deepslate_bricks");
        if (y <= 100) {
            if (dist > 2) return T("cobbled_deepslate");
            if (north && hash(x, y, z, 81) < 0.12) return T("packed_ice");
            return north ? pick(x, y, z, 82, 25, "deepslate_bricks", 15, "polished_deepslate", 30, "cobbled_deepslate", 5, "deepslate_tiles", 25, "cracked_deepslate_bricks")
                         : pick(x, y, z, 83, 35, "deepslate_bricks", 20, "polished_deepslate", 20, "cobbled_deepslate", 15, "deepslate_tiles", 10, "cracked_deepslate_bricks");
        }
        if (y >= 213) return T("packed_ice");
        if (dist <= 2) {
            int yy = y - 100; int period = 14; int ph = (int) (hash(x / 40, 0, 0, 84) * 3);
            if (dist == 0 && Math.floorMod(yy + ph, period) == 0) return hash(x, y, z, 85) < 0.6 ? T("smooth_basalt") : T("tuff");
            if (dist == 0) return pick(x, y, z, 86, 55, "packed_ice", 25, "blue_ice", 10, "ice", 10, "snow_block");
            return pick(x, y, z, 87, 70, "packed_ice", 30, "blue_ice");
        }
        return T("packed_ice");
    }

    static void apply(Path world, Path grid) throws Exception {
        ByteBuffer bb; try (FileChannel fc = FileChannel.open(grid)) { bb = ByteBuffer.allocate((int) fc.size()).order(ByteOrder.LITTLE_ENDIAN); while (bb.hasRemaining() && fc.read(bb) > 0) {} }
        bb.flip(); byte[] mg = new byte[4]; bb.get(mg); if (!new String(mg).equals("LETA")) throw new IOException("not a grid file");
        int x0 = bb.getInt(), z0 = bb.getInt(), w = bb.getInt(), h = bb.getInt(), n = w * h;
        short[] H = new short[n], F = new short[n], W = new short[n]; byte[] S = new byte[n], R = new byte[n], A = new byte[n];
        for (int i = 0; i < n; i++) H[i] = bb.getShort(); for (int i = 0; i < n; i++) F[i] = bb.getShort(); for (int i = 0; i < n; i++) W[i] = bb.getShort();
        bb.get(S); bb.get(R); bb.get(A);
        long t0 = System.currentTimeMillis(); int chunks = 0, missing = 0; long cols = 0, bes = 0, ents = 0;
        try (RegionFileStorage st = open(world, "chunk"); RegionFileStorage es = open(world, "entities")) {
            for (int cz = Math.floorDiv(z0, 16); cz <= Math.floorDiv(z0 + h - 1, 16); cz++) for (int cx = Math.floorDiv(x0, 16); cx <= Math.floorDiv(x0 + w - 1, 16); cx++) {
                boolean any = false; int[] lowest = new int[256]; Arrays.fill(lowest, Integer.MAX_VALUE);
                for (int lz = 0; lz < 16; lz++) for (int lx = 0; lx < 16; lx++) {
                    int x = cx * 16 + lx, z = cz * 16 + lz; if (x < x0 || z < z0 || x >= x0 + w || z >= z0 + h) continue;
                    int i = (z - z0) * w + (x - x0); if (H[i] != NONE) { any = true; lowest[lz * 16 + lx] = Math.max(MINY, F[i]); }
                }
                if (!any) continue;
                ChunkPos cp = new ChunkPos(cx, cz); CompoundTag ch = st.read(cp);
                if (ch == null || !ch.getStringOr("Status", "").endsWith("full")) { missing++; continue; }
                Map<Integer, Integer> yToIdx = new HashMap<>(); Tag[][] b = sections(ch, yToIdx); Tag[] col = new Tag[MAXY - MINY + 1];
                for (int lz = 0; lz < 16; lz++) for (int lx = 0; lx < 16; lx++) {
                    if (lowest[lz * 16 + lx] == Integer.MAX_VALUE) continue;
                    int x = cx * 16 + lx, z = cz * 16 + lz, i = (z - z0) * w + (x - x0), fl = lowest[lz * 16 + lx];
                    column(col, x, z, H[i], fl, W[i], S[i] & 255, R[i] & 255, A[i] & 255);
                    for (int y = fl; y <= MAXY; y++) put(b, lx, y, lz, col[y - MINY]);
                    cols++;
                }
                ListTag secs = ch.getListOrEmpty("sections");
                for (int s = 0; s < 24; s++) {
                    Integer i = yToIdx.get(s - 4); CompoundTag sec;
                    if (i == null) { sec = new CompoundTag(); sec.putByte("Y", (byte) (s - 4)); secs.add(sec); yToIdx.put(s - 4, secs.size() - 1);
                        for (int q = s - 1; q >= 0; q--) { Integer j = yToIdx.get(q - 4); if (j == null) continue;   // a new section takes the biomes of the one below
                            CompoundTag bio = secs.getCompoundOrEmpty(j).getCompoundOrEmpty("biomes"); if (!bio.getListOrEmpty("palette").isEmpty()) { sec.put("biomes", bio.copy()); break; } }
                    } else sec = secs.getCompoundOrEmpty(i);
                    encode(sec, b[s]);
                }
                ListTag keep = new ListTag();
                for (Tag t : ch.getListOrEmpty("block_entities")) { CompoundTag c = (CompoundTag) t; int lx = c.getIntOr("x", 0) & 15, lz = c.getIntOr("z", 0) & 15;
                    if (c.getIntOr("y", 0) >= lowest[lz * 16 + lx]) bes++; else keep.add(c); }
                ch.put("block_entities", keep);
                for (String tk : new String[]{"block_ticks", "fluid_ticks"}) { ListTag kt = new ListTag();
                    for (Tag t : ch.getListOrEmpty(tk)) { CompoundTag c = (CompoundTag) t; int lx = c.getIntOr("x", 0) & 15, lz = c.getIntOr("z", 0) & 15; if (c.getIntOr("y", 0) < lowest[lz * 16 + lx]) kt.add(c); }
                    ch.put(tk, kt); }
                ch.putBoolean("isLightOn", false); ch.remove("Heightmaps"); st.write(cp, ch); chunks++;
                CompoundTag e = es.read(cp);
                if (e != null) { ListTag keepE = new ListTag();
                    for (Tag t : e.getListOrEmpty("Entities")) { CompoundTag c = (CompoundTag) t; ListTag p = c.getListOrEmpty("Pos");
                        int ex = (int) Math.floor(p.getDoubleOr(0, 0)), ey = (int) Math.floor(p.getDoubleOr(1, 0)), ez = (int) Math.floor(p.getDoubleOr(2, 0));
                        if (Math.floorDiv(ex, 16) == cx && Math.floorDiv(ez, 16) == cz && ey >= lowest[(ez & 15) * 16 + (ex & 15)]) ents++; else keepE.add(c); }
                    e.put("Entities", keepE); es.write(cp, e); }
            }
        }
        System.out.printf("apply: %d columns in %d chunks (%d missing/unfinished), removed %d block entities and %d entities, %.1fs%n", cols, chunks, missing, bes, ents, (System.currentTimeMillis() - t0) / 1000.0);
        if (missing > 0) { System.out.println("ERROR: chunks missing (generate them first)"); System.exit(2); }
    }
}
