import java.io.*;
import java.nio.file.*;
import java.util.*;

import net.minecraft.SharedConstants;
import net.minecraft.commands.arguments.blocks.BlockStateParser;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.*;
import net.minecraft.server.Bootstrap;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.storage.RegionFileStorage;
import net.minecraft.world.level.chunk.storage.RegionStorageInfo;

/**
 * T-008 builder backend (server STOPPED). Placement files: one block per line "x y z state[props]{nbt}" (nbt optional, merged
 * into the block entity). States are validated with the game's own parser.
 *   BlockWriter apply <world> <file...>                      write blocks (+ block entities) into region files, drop light/heightmaps
 *   BlockWriter nbt <file> <ox> <oy> <oz> <out.nbt>          the same blocks as a structure template (origin = min corner)
 *   BlockWriter heights <world> <x1> <z1> <x2> <z2> <out>    ground height per column ("x z y" lines; trees and plants ignored)
 */
public class BlockWriter {
    static final int MINY = -64;
    record P(int x, int y, int z, BlockState st, CompoundTag nbt, String raw) {}
    static final Map<String, BlockState> CACHE = new HashMap<>();

    static List<P> read(Path f) throws Exception {
        List<P> out = new ArrayList<>(); int ln = 0;
        for (String line : Files.readAllLines(f)) {
            ln++; line = line.strip(); if (line.isEmpty() || line.startsWith("#")) continue;
            String[] a = line.split(" ", 4);
            String s = a[3]; BlockStateParser.BlockResult r;
            try { r = BlockStateParser.parseForBlock(BuiltInRegistries.BLOCK, s, true); }
            catch (Exception e) { throw new RuntimeException(f + ":" + ln + ": bad block state '" + s + "': " + e.getMessage()); }
            out.add(new P(Integer.parseInt(a[0]), Integer.parseInt(a[1]), Integer.parseInt(a[2]), r.blockState(), r.nbt(), s));
        }
        return out;
    }
    static Tag paletteEntry(BlockState st) {
        CompoundTag t = NbtUtils.writeBlockState(st);   // 26.x: {id, properties}
        String name = t.getString("id").orElseThrow(() -> new IllegalStateException("no id in " + t));
        CompoundTag props = t.getCompoundOrEmpty("properties");
        if (props.isEmpty()) return StringTag.valueOf(name);
        CompoundTag c = new CompoundTag(); c.putString("id", name); c.put("properties", props); return c;
    }
    static Tag[] decode(CompoundTag sec) {
        Tag[] out = new Tag[4096]; CompoundTag bs = sec.getCompoundOrEmpty("block_states"); ListTag pal = bs.getListOrEmpty("palette");
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
    static CompoundTag blockEntity(P p) {
        if (!p.st.hasBlockEntity() || !(p.st.getBlock() instanceof EntityBlock eb)) return null;
        BlockEntity be = eb.newBlockEntity(new BlockPos(p.x, p.y, p.z), p.st); if (be == null) return null;
        CompoundTag t = new CompoundTag(); t.putString("id", BuiltInRegistries.BLOCK_ENTITY_TYPE.getKey(be.getType()).toString());
        t.putInt("x", p.x); t.putInt("y", p.y); t.putInt("z", p.z); t.putBoolean("keepPacked", false);
        if (p.nbt != null) t.merge(p.nbt);
        return t;
    }

    public static void main(String[] a) throws Exception {
        SharedConstants.tryDetectVersion(); Bootstrap.bootStrap();
        switch (a[0]) {
            case "apply" -> apply(Paths.get(a[1]), Arrays.copyOfRange(a, 2, a.length));
            case "nbt" -> nbt(Paths.get(a[1]), Integer.parseInt(a[2]), Integer.parseInt(a[3]), Integer.parseInt(a[4]), Paths.get(a[5]));
            case "heights" -> heights(Paths.get(a[1]), Integer.parseInt(a[2]), Integer.parseInt(a[3]), Integer.parseInt(a[4]), Integer.parseInt(a[5]), Paths.get(a[6]));
            default -> throw new IllegalArgumentException(a[0]);
        }
    }

    static void apply(Path world, String[] files) throws Exception {
        long t0 = System.currentTimeMillis(); Map<Long, List<P>> byChunk = new HashMap<>(); int n = 0;
        for (String f : files) for (P p : read(Paths.get(f))) { byChunk.computeIfAbsent((((long) Math.floorDiv(p.x, 16)) << 32) | (Math.floorDiv(p.z, 16) & 0xffffffffL), k -> new ArrayList<>()).add(p); n++; }
        int chunks = 0, missing = 0, bes = 0;
        try (RegionFileStorage st = new RegionFileStorage(new RegionStorageInfo("world", Level.OVERWORLD, "chunk"), world.resolve("dimensions/minecraft/overworld/region"), false)) {
            for (var e : byChunk.entrySet()) {
                int cx = (int) (e.getKey() >> 32), cz = (int) (long) e.getKey().intValue(); ChunkPos cp = new ChunkPos(cx, cz);
                CompoundTag ch = st.read(cp); if (ch == null) { missing++; continue; }
                ListTag secs = ch.getListOrEmpty("sections"); Tag[][] blocks = new Tag[secs.size()][]; Map<Integer, Integer> yToIdx = new HashMap<>();
                for (int i = 0; i < secs.size(); i++) { yToIdx.put((int) secs.getCompoundOrEmpty(i).getByteOr("Y", (byte) 0), i); }
                Map<String, CompoundTag> bemap = new LinkedHashMap<>();
                for (Tag t : ch.getListOrEmpty("block_entities")) { CompoundTag c = (CompoundTag) t; bemap.put(c.getIntOr("x", 0) + "," + c.getIntOr("y", 0) + "," + c.getIntOr("z", 0), c); }
                for (P p : e.getValue()) {
                    Integer si = yToIdx.get(Math.floorDiv(p.y, 16)); if (si == null) continue;
                    if (blocks[si] == null) blocks[si] = decode(secs.getCompoundOrEmpty(si));
                    blocks[si][((p.y & 15) << 8) | ((p.z & 15) << 4) | (p.x & 15)] = paletteEntry(p.st);
                    String key = p.x + "," + p.y + "," + p.z; bemap.remove(key);
                    CompoundTag be = blockEntity(p); if (be != null) { bemap.put(key, be); bes++; }
                }
                for (int i = 0; i < blocks.length; i++) if (blocks[i] != null) encode(secs.getCompoundOrEmpty(i), blocks[i]);
                ListTag bel = new ListTag(); bel.addAll(bemap.values()); ch.put("block_entities", bel);
                ch.putBoolean("isLightOn", false); ch.remove("Heightmaps"); st.write(cp, ch); chunks++;
            }
        }
        System.out.printf("apply: %d blocks, %d block entities, %d chunks written, %d chunks missing, %.1fs%n", n, bes, chunks, missing, (System.currentTimeMillis() - t0) / 1000.0);
        if (missing > 0) { System.out.println("ERROR: chunks missing (generate them first)"); System.exit(2); }
    }

    static void nbt(Path f, int ox, int oy, int oz, Path out) throws Exception {
        List<P> ps = read(f); int sx = 0, sy = 0, sz = 0; LinkedHashMap<String, Integer> pm = new LinkedHashMap<>(); ListTag pal = new ListTag(), blocks = new ListTag();
        for (P p : ps) {
            int x = p.x - ox, y = p.y - oy, z = p.z - oz; if (x < 0 || y < 0 || z < 0) throw new RuntimeException("block below origin: " + p);
            sx = Math.max(sx, x + 1); sy = Math.max(sy, y + 1); sz = Math.max(sz, z + 1);
            CompoundTag st = NbtUtils.writeBlockState(p.st); String k = st.toString(); Integer i = pm.get(k); if (i == null) { i = pm.size(); pm.put(k, i); pal.add(st); }
            CompoundTag b = new CompoundTag(); ListTag pos = new ListTag(); pos.add(IntTag.valueOf(x)); pos.add(IntTag.valueOf(y)); pos.add(IntTag.valueOf(z)); b.put("pos", pos); b.putInt("state", i);
            CompoundTag be = blockEntity(p); if (be != null) { be.remove("x"); be.remove("y"); be.remove("z"); b.put("nbt", be); }
            blocks.add(b);
        }
        CompoundTag root = new CompoundTag(); ListTag size = new ListTag(); size.add(IntTag.valueOf(sx)); size.add(IntTag.valueOf(sy)); size.add(IntTag.valueOf(sz));
        root.put("size", size); root.put("palette", pal); root.put("blocks", blocks); root.put("entities", new ListTag()); NbtUtils.addCurrentDataVersion(root);
        Files.createDirectories(out.getParent()); NbtIo.writeCompressed(root, out);
        System.out.printf("nbt: %s %dx%dx%d, %d blocks, %d palette%n", out, sx, sy, sz, blocks.size(), pal.size());
    }

    static final Set<String> SKIP = new HashSet<>(Arrays.asList("air", "cave_air", "water", "lava", "short_grass", "tall_grass", "fern", "large_fern", "snow", "vine",
        "dead_bush", "bush", "leaf_litter", "wildflowers", "sugar_cane", "seagrass", "tall_seagrass", "kelp", "kelp_plant", "sweet_berry_bush", "firefly_bush", "short_dry_grass", "tall_dry_grass", "pumpkin"));
    static boolean ground(Tag t) {
        String n = (t instanceof StringTag s ? s.value() : ((CompoundTag) t).getStringOr("id", "?")).replace("minecraft:", "");
        if (SKIP.contains(n)) return false;
        return !(n.endsWith("leaves") || n.endsWith("_log") || n.endsWith("_wood") || n.contains("flower") || n.contains("tulip") || n.contains("mushroom") || n.endsWith("sapling")
            || n.equals("poppy") || n.equals("dandelion") || n.contains("orchid") || n.contains("allium") || n.contains("bluet") || n.contains("daisy") || n.contains("lily") || n.contains("rose") || n.equals("lilac") || n.equals("peony") || n.endsWith("_stem") || n.contains("cornflower") || n.equals("cactus") || n.equals("bamboo") || n.equals("moss_carpet") || n.contains("dripleaf") || n.equals("cocoa"));
    }
    static void heights(Path world, int x1, int z1, int x2, int z2, Path out) throws Exception {
        StringBuilder sb = new StringBuilder(); Map<Long, Tag[][]> cache = new HashMap<>();
        try (RegionFileStorage st = new RegionFileStorage(new RegionStorageInfo("world", Level.OVERWORLD, "chunk"), world.resolve("dimensions/minecraft/overworld/region"), false)) {
            for (int x = x1; x <= x2; x++) for (int z = z1; z <= z2; z++) {
                int cx = Math.floorDiv(x, 16), cz = Math.floorDiv(z, 16); long key = (((long) cx) << 32) | (cz & 0xffffffffL);
                Tag[][] secs = cache.get(key);
                if (secs == null) { CompoundTag ch = st.read(new ChunkPos(cx, cz)); if (ch == null) { secs = new Tag[0][]; } else { ListTag l = ch.getListOrEmpty("sections"); secs = new Tag[l.size()][]; for (int i = 0; i < l.size(); i++) secs[i] = decode(l.getCompoundOrEmpty(i)); } cache.put(key, secs); }
                int y = Integer.MIN_VALUE;
                for (int yy = MINY + secs.length * 16 - 1; yy >= MINY && secs.length > 0; yy--) { Tag t = secs[(yy - MINY) >> 4][(((yy - MINY) & 15) << 8) | ((z & 15) << 4) | (x & 15)]; if (ground(t)) { y = yy; break; } }
                sb.append(x).append(' ').append(z).append(' ').append(y).append('\n');
            }
        }
        Files.writeString(out, sb.toString()); System.out.println("heights written: " + out);
    }
}
