import com.google.gson.*;
import java.awt.image.BufferedImage;
import java.io.*;
import java.nio.file.*;
import java.util.*;
import javax.imageio.ImageIO;

import net.minecraft.SharedConstants;
import net.minecraft.nbt.*;
import net.minecraft.server.Bootstrap;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.chunk.storage.RegionFileStorage;
import net.minecraft.world.level.chunk.storage.RegionStorageInfo;

/**
 * Heightmap sculptor (T-003). Writes terrain from a grayscale PNG straight into the world's region files (server STOPPED).
 *   Sculpt apply  <worldDir> <spec.json>
 *   Sculpt verify <worldDir> <spec.json> <profiles.csv>
 * Inside the footprint every column is rebuilt from bedrock to the build limit (everything generated is removed); in a seam strip
 * of seamWidth blocks outside the footprint the height is blended into the existing generated terrain. Biomes are kept.
 * Light data is dropped (isLightOn=false) so the server relights chunks on load; heightmaps are dropped and rebuilt by the server.
 */
public class Sculpt {
    static final int MINY = -64, MAXY = 319;
    static JsonObject spec; static int x0, z0, w, h, offY, seam; static int[][] H0; // [x][z] top solid block Y
    static double cx, cz; static Path dimDir;

    public static void main(String[] a) throws Exception {
        SharedConstants.tryDetectVersion(); Bootstrap.bootStrap();
        Path world = Paths.get(a[1]); spec = JsonParser.parseReader(new FileReader(a[2])).getAsJsonObject();
        dimDir = world.resolve("dimensions/minecraft/overworld");
        Path png = Paths.get(spec.get("png").getAsString());
        BufferedImage img = ImageIO.read(png.toFile()); w = img.getWidth(); h = img.getHeight();
        x0 = spec.get("x0").getAsInt(); z0 = spec.get("z0").getAsInt(); offY = spec.get("offsetY").getAsInt(); seam = spec.get("seamWidth").getAsInt();
        cx = spec.getAsJsonArray("center").get(0).getAsDouble(); cz = spec.getAsJsonArray("center").get(1).getAsDouble();
        H0 = new int[w][h];
        for (int x = 0; x < w; x++) for (int z = 0; z < h; z++) H0[x][z] = (img.getRaster().getSample(x, z, 0)) + offY;
        if (a[0].equals("apply")) apply(); else verify(a[3]);
    }

    // ---------- geometry ----------
    static boolean inside(int x, int z) { return x >= x0 && x < x0 + w && z >= z0 && z < z0 + h; }
    static double distOutside(int x, int z) {
        double dx = Math.max(Math.max(x0 - x, 0), x - (x0 + w - 1)), dz = Math.max(Math.max(z0 - z, 0), z - (z0 + h - 1));
        return Math.hypot(dx, dz);
    }
    static int pix(int x, int z) { return H0[Math.max(0, Math.min(w - 1, x - x0))][Math.max(0, Math.min(h - 1, z - z0))]; }

    // ---------- noise ----------
    static double hash(int x, int z, int salt) {
        long n = x * 374761393L + z * 668265263L + salt * 1442695040888963407L; n = (n ^ (n >>> 13)) * 1274126177L; n ^= n >>> 16;
        return ((n & 0xffffff) / (double) 0x1000000);
    }
    static double vnoise(double x, double z, int salt) {
        int xi = (int) Math.floor(x), zi = (int) Math.floor(z); double fx = x - xi, fz = z - zi;
        fx = fx * fx * (3 - 2 * fx); fz = fz * fz * (3 - 2 * fz);
        double a = hash(xi, zi, salt), b = hash(xi + 1, zi, salt), c = hash(xi, zi + 1, salt), d = hash(xi + 1, zi + 1, salt);
        return (a * (1 - fx) + b * fx) * (1 - fz) + (c * (1 - fx) + d * fx) * fz;
    }

    // ---------- blocks ----------
    static final Map<String, Tag> TAGS = new HashMap<>();
    static Tag T(String n) { return TAGS.computeIfAbsent(n, k -> StringTag.valueOf("minecraft:" + k)); }
    static String nameOf(Tag t) { if (t instanceof StringTag s) return s.value(); return ((CompoundTag) t).getStringOr("id", "?"); }
    static final Set<String> GROUND = new HashSet<>(Arrays.asList("stone", "dirt", "grass_block", "sand", "gravel", "sandstone", "podzol", "coarse_dirt", "rooted_dirt", "mud", "clay",
        "red_sand", "red_sandstone", "terracotta", "snow_block", "powder_snow", "deepslate", "tuff", "andesite", "diorite", "granite", "mycelium", "moss_block", "calcite", "packed_ice", "ice", "blue_ice",
        "netherrack", "bedrock", "mangrove_roots", "muddy_mangrove_roots", "dripstone_block", "amethyst_block", "smooth_basalt", "basalt", "white_terracotta", "orange_terracotta", "yellow_terracotta",
        "red_terracotta", "brown_terracotta", "light_gray_terracotta"));

    /** composes one column; returns Tag per y (index y-MINY) */
    static Tag[] column(int x, int z, int H, double slope) {
        Tag[] c = new Tag[MAXY - MINY + 1]; Tag air = T("air");
        Arrays.fill(c, air);
        double lakeX = spec.getAsJsonObject("lake").get("x").getAsDouble(), lakeZ = spec.getAsJsonObject("lake").get("z").getAsDouble();
        double lakeR = spec.getAsJsonObject("lake").get("r").getAsDouble(); int lakeY = spec.getAsJsonObject("lake").get("level").getAsInt();
        int snow = spec.get("snowLine").getAsInt(), stoneLine = spec.get("stoneLine").getAsInt(); double valleyR = spec.get("valleyRadius").getAsDouble();
        double rLake = Math.hypot(x - lakeX, z - lakeZ), rC = Math.hypot(x - cx, z - cz);
        boolean lake = rLake <= lakeR && H < lakeY;
        for (int y = MINY; y <= H; y++) {
            Tag b;
            if (y <= MINY + 4 && (y == MINY || hash(x, z, y) < 0.8 - (y - MINY) * 0.2)) b = T("bedrock");
            else if (y < 0 - (int) (hash(x >> 1, z >> 1, 7) * 6)) b = T("deepslate");
            else b = T("stone");
            c[y - MINY] = b;
        }
        // surface cover
        for (int y = Math.max(H - 3, MINY + 5); y <= H; y++) {
            int depth = H - y; Tag b = null;
            if (lake) {
                double n = hash(x, z, 11);
                b = depth == 0 ? (n < 0.5 ? T("gravel") : n < 0.8 ? T("clay") : T("dirt")) : (depth < 3 ? T("dirt") : null);
            } else if (H >= snow) {
                if (depth == 0) b = (hash(x, z, 21) < 0.12 && slope < 0.8 && vnoise(x / 9.0, z / 9.0, 22) > 0.55) ? T("powder_snow") : T("snow_block");
                else if (depth < 3) b = T("snow_block");
            } else if (H >= stoneLine) {
                b = null; // strata applied below
            } else {
                boolean valley = rC < valleyR;
                if (slope > 1.4 && depth < 2) b = vnoise(x / 5.0, z / 5.0, 31) > 0.45 ? T("stone") : T("andesite");
                else if (depth == 0) b = valley ? (vnoise(x / 7.0, z / 7.0, 41) > 0.68 ? T("moss_block") : T("grass_block")) : T("grass_block")  /* T-003 review: no gravel patches on the outer apron */;
                else if (depth < 3) b = T("dirt");
            }
            if (b != null) c[y - MINY] = b;
        }
        if (H >= stoneLine && H < snow) { // cliff strata: stone / andesite / tuff / calcite in height bands
            Tag[] bands = {T("stone"), T("andesite"), T("tuff"), T("stone"), T("calcite"), T("andesite")};
            double ph = vnoise(x / 24.0, z / 24.0, 51) * 6;
            for (int y = stoneLine; y <= H; y++) c[y - MINY] = bands[(int) Math.floor((y + ph) / 4.0 + hash(x / 6, z / 6, 52) * 0.9) % 6 < 0 ? 0 : (int) Math.floor((y + ph) / 4.0 + hash(x / 6, z / 6, 52) * 0.9) % 6];
        }
        if (H >= snow) for (int y = stoneLine; y < H - 2; y++) { // exposed rock below the snow cap keeps strata
            if (y >= snow - 6) continue; Tag[] bands = {T("stone"), T("andesite"), T("tuff"), T("calcite")};
            c[y - MINY] = bands[(int) Math.floor((y + vnoise(x / 24.0, z / 24.0, 51) * 6) / 4.0) & 3];
        }
        if (lake) for (int y = H + 1; y <= lakeY; y++) c[y - MINY] = T("water");
        return c;
    }

    static double slopeAt(int x, int z) {
        double dx = (pix(x + 2, z) - pix(x - 2, z)) / 4.0, dz = (pix(x, z + 2) - pix(x, z - 2)) / 4.0;
        return Math.hypot(dx, dz);
    }

    // ---------- chunk io ----------
    static Tag[] decode(CompoundTag sec) {
        Tag[] out = new Tag[4096];
        CompoundTag bs = sec.getCompoundOrEmpty("block_states"); ListTag pal = bs.getListOrEmpty("palette");
        long[] data = bs.getLongArray("data").orElse(null);
        if (data == null || pal.size() == 1) { Arrays.fill(out, pal.get(0)); return out; }
        int bits = Math.max(4, 32 - Integer.numberOfLeadingZeros(pal.size() - 1)), per = 64 / bits; long mask = (1L << bits) - 1;
        for (int i = 0; i < 4096; i++) out[i] = pal.get((int) ((data[i / per] >>> ((i % per) * bits)) & mask));
        return out;
    }
    static CompoundTag encode(Tag[] blocks, CompoundTag oldSec, int yIndex) {
        LinkedHashMap<String, Integer> pm = new LinkedHashMap<>(); ListTag pal = new ListTag(); int[] idx = new int[4096];
        for (int i = 0; i < 4096; i++) { String k = blocks[i].toString(); Integer p = pm.get(k); if (p == null) { p = pm.size(); pm.put(k, p); pal.add(blocks[i]); } idx[i] = p; }
        CompoundTag bs = new CompoundTag(); bs.put("palette", pal);
        if (pal.size() > 1) {
            int bits = Math.max(4, 32 - Integer.numberOfLeadingZeros(pal.size() - 1)), per = 64 / bits; long[] data = new long[(4096 + per - 1) / per];
            for (int i = 0; i < 4096; i++) data[i / per] |= ((long) idx[i]) << ((i % per) * bits);
            bs.put("data", new LongArrayTag(data));
        }
        CompoundTag sec = new CompoundTag();
        sec.put("block_states", bs); sec.put("biomes", oldSec.get("biomes")); sec.put("Y", ByteTag.valueOf((byte) (yIndex - 4)));
        return sec;
    }

    static void apply() throws Exception {
        int cMinX = Math.floorDiv(x0 - seam, 16), cMaxX = Math.floorDiv(x0 + w - 1 + seam, 16), cMinZ = Math.floorDiv(z0 - seam, 16), cMaxZ = Math.floorDiv(z0 + h - 1 + seam, 16);
        long t0 = System.currentTimeMillis(); int chunks = 0, missing = 0; long colsNew = 0, colsSeam = 0; int worstSeamStep = 0;
        Path regionDir = dimDir.resolve("region"), entDir = dimDir.resolve("entities");
        try (RegionFileStorage st = new RegionFileStorage(new RegionStorageInfo("world", Level.OVERWORLD, "chunk"), regionDir, false);
             RegionFileStorage ents = Files.isDirectory(entDir) ? new RegionFileStorage(new RegionStorageInfo("world", Level.OVERWORLD, "entities"), entDir, false) : null) {
            for (int czk = cMinZ; czk <= cMaxZ; czk++) for (int cxk = cMinX; cxk <= cMaxX; cxk++) {
                ChunkPos cp = new ChunkPos(cxk, czk); CompoundTag ch = st.read(cp);
                if (ch == null) { missing++; continue; }
                ListTag secs = ch.getListOrEmpty("sections"); Tag[][] blocks = new Tag[24][]; for (int i = 0; i < 24; i++) blocks[i] = decode(secs.getCompoundOrEmpty(i));
                boolean touched = false;
                for (int lz = 0; lz < 16; lz++) for (int lx = 0; lx < 16; lx++) {
                    int x = cxk * 16 + lx, z = czk * 16 + lz; double d = distOutside(x, z);
                    if (d > seam) continue;
                    int H; double slope;
                    if (d == 0) { H = pix(x, z); slope = slopeAt(x, z); colsNew++; }
                    else { // seam: blend from the edge height into the existing generated ground
                        int G = existingTop(blocks, lx, lz); double t = 1 - Math.min(1, d / seam); int E = pix(x, z);  // linear blend: gentlest worst-case slope
                        H = (int) Math.round(t * E + (1 - t) * G); slope = 0; colsSeam++;
                    }
                    Tag[] col = column(x, z, H, slope);
                    for (int y = MINY; y <= MAXY; y++) { int s = (y - MINY) >> 4, i = (((y - MINY) & 15) << 8) | (lz << 4) | lx; blocks[s][i] = col[y - MINY]; }
                    touched = true;
                }
                if (!touched) continue;
                ListTag ns = new ListTag(); for (int i = 0; i < 24; i++) ns.add(encode(blocks[i], secs.getCompoundOrEmpty(i), i));
                ch.put("sections", ns); ch.putBoolean("isLightOn", false); ch.remove("Heightmaps");
                ch.put("block_entities", new ListTag()); ch.put("block_ticks", new ListTag()); ch.put("fluid_ticks", new ListTag()); ch.put("PostProcessing", new ListTag());
                st.write(cp, ch); chunks++;
                if (ents != null) { CompoundTag e = ents.read(cp); if (e != null) { e.put("Entities", new ListTag()); ents.write(cp, e); } }
            }
        }
        System.out.printf("apply: %d chunks rewritten (%d missing), %d footprint columns, %d seam columns, %.1fs%n", chunks, missing, colsNew, colsSeam, (System.currentTimeMillis() - t0) / 1000.0);
        if (missing > 0) { System.out.println("ERROR: " + missing + " chunks missing: generate the area first (forceload), then re-run"); System.exit(2); }
    }
    static double smooth(double t) { t = Math.max(0, Math.min(1, t)); return t * t * (3 - 2 * t); }
    static int existingTop(Tag[][] blocks, int lx, int lz) {
        for (int y = MAXY; y >= MINY; y--) { Tag b = blocks[(y - MINY) >> 4][(((y - MINY) & 15) << 8) | (lz << 4) | lx]; if (GROUND.contains(nameOf(b).replace("minecraft:", ""))) return y; }
        return 63;
    }

    // ---------- verification ----------
    static int groundTop(RegionFileStorage st, Map<Long, Tag[][]> cache, int x, int z) throws IOException {
        int cxk = Math.floorDiv(x, 16), czk = Math.floorDiv(z, 16); long key = (((long) cxk << 32) | (czk & 0xffffffffL));
        Tag[][] blocks = cache.get(key);
        if (blocks == null) { CompoundTag ch = st.read(new ChunkPos(cxk, czk)); if (ch == null) return Integer.MIN_VALUE; ListTag secs = ch.getListOrEmpty("sections"); blocks = new Tag[24][]; for (int i = 0; i < 24; i++) blocks[i] = decode(secs.getCompoundOrEmpty(i)); cache.put(key, blocks); }
        int lx = Math.floorMod(x, 16), lz = Math.floorMod(z, 16);
        for (int y = MAXY; y >= MINY; y--) { String n = nameOf(blocks[(y - MINY) >> 4][(((y - MINY) & 15) << 8) | (lz << 4) | lx]).replace("minecraft:", ""); if (GROUND.contains(n)) return y; }  // terrain only: trees, plants and water are ignored
        return MINY;
    }
    static void verify(String csv) throws Exception {
        List<String> lines = Files.readAllLines(Paths.get(csv)); String[] head = lines.get(0).split(",");
        Map<Long, Tag[][]> cache = new HashMap<>();
        try (RegionFileStorage st = new RegionFileStorage(new RegionStorageInfo("world", Level.OVERWORLD, "chunk"), dimDir.resolve("region"), false)) {
            int tol = spec.has("tolerance") ? spec.get("tolerance").getAsInt() : 3; boolean allOk = true;
            for (int li = 1; li < lines.size(); li++) {
                String[] f = lines.get(li).split(","); double az = Math.toRadians(Double.parseDouble(f[1])); int maxd = 0, n = 0; double sumAbs = 0;
                for (int k = 2; k < f.length; k++) {
                    int r = (k - 2) * 5; int x = (int) Math.round(cx + r * Math.sin(az)), z = (int) Math.round(cz - r * Math.cos(az));
                    int expect = Integer.parseInt(f[k]), got = groundTop(st, cache, x, z); int dd = Math.abs(got - expect); if (dd > maxd) maxd = dd; sumAbs += dd; n++;
                }
                boolean ok = maxd <= tol; allOk &= ok;
                System.out.printf("%-12s az %3s: max|diff| %2d  mean %.2f  %s%n", f[0], f[1], maxd, sumAbs / n, ok ? "OK" : "OUT OF TOLERANCE");
            }
            // seam: largest height step between horizontally adjacent ground columns along a ring around the footprint, 0..seam out
            int worst = 0; String where = "";
            int worstOuter = 0; String whereOuter = ""; long pairs = 0, over4 = 0; long[] perD = new long[seam + 4]; long[] perSide = new long[4];
            for (int d = -2; d <= seam; d++) {
                for (int side = 0; side < 4; side++) for (int t = 0; t < (side % 2 == 0 ? h : w); t++) {
                    int xa, za, xb, zb;
                    switch (side) { case 0 -> { xa = x0 - d; za = z0 + t; xb = xa - 1; zb = za; } case 1 -> { xa = x0 + t; za = z0 - d; xb = xa; zb = za - 1; }
                        case 2 -> { xa = x0 + w - 1 + d; za = z0 + t; xb = xa + 1; zb = za; } default -> { xa = x0 + t; za = z0 + h - 1 + d; xb = xa; zb = za + 1; } }
                    int ya = groundTop(st, cache, xa, za), yb = groundTop(st, cache, xb, zb); if (ya == Integer.MIN_VALUE || yb == Integer.MIN_VALUE) continue;
                    int step = Math.abs(ya - yb);
                    if (d < seam) { pairs++; if (step > 4) { over4++; perD[d + 2]++; perSide[side]++; } if (step > worst) { worst = step; where = "(" + xa + "," + za + ")->(" + xb + "," + zb + ") d=" + d; } }
                    else if (step > worstOuter) { worstOuter = step; whereOuter = "(" + xa + "," + za + ")->(" + xb + "," + zb + ")"; }
                }
            }
            System.out.println("seam: largest step between adjacent ground columns inside the strip (d=-2.." + (seam - 1) + "): " + worst + " blocks at " + where + (worst <= 4 ? "  OK" : "  > 4"));
            System.out.println("seam: steps>4 by d(-2..): " + Arrays.toString(perD) + " by side(W,N,E,S): " + Arrays.toString(perSide));
            System.out.println("seam: strip pairs checked " + pairs + ", with step > 4: " + over4);
            System.out.println("seam: step across the strip's outer edge (strip vs untouched generation, includes natural cliffs): " + worstOuter + " blocks at " + whereOuter);
            System.out.println(allOk ? "PROFILES OK" : "PROFILES OUT OF TOLERANCE");
        }
    }
}
