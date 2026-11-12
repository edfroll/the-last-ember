import java.nio.file.*;
import java.util.*;

import net.minecraft.SharedConstants;
import net.minecraft.commands.arguments.blocks.BlockStateParser;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.*;
import net.minecraft.server.Bootstrap;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.EmptyBlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.chunk.storage.RegionFileStorage;
import net.minecraft.world.level.chunk.storage.RegionStorageInfo;

/**
 * T-021 region borders (server STOPPED). The border lines come from gates/borders.gen.json (tools/gen_gates.py).
 *   Borders apply <world> <borders.json> [id...]      every block of the axis plane (y -64..319, outside the gaps) that is not a full
 *                                                      collision block (air, water, lava, plants, snow layers, doors, slabs...) becomes
 *                                                      barrier (waterlogged where there was water); full blocks stay. Safe to repeat.
 *   Borders holes <world> <borders.json> <out> [id...] per border: the passable cells left on the axis outside the gaps
 *   Borders wallmap <world> <x1> <z1> <x2> <z2> <out>  per column 1 = closed from y -64 to 319 (all full collision), else 0
 * Chunks that do not exist yet or are not finished (proto-chunks round the generated area) are skipped and listed.
 */
public class Borders {
    static final int MINY = -64, MAXY = 319;
    static final Map<String, BlockState> CACHE = new HashMap<>();
    static final Map<String, Boolean> FULL = new HashMap<>();

    static String key(Tag t) {
        if (t instanceof StringTag s) return s.value();
        CompoundTag c = (CompoundTag) t;
        String id = c.getString("id").orElseGet(() -> c.getStringOr("", "minecraft:air"));
        CompoundTag p = c.getCompoundOrEmpty("properties");
        if (p.isEmpty()) return id;
        StringJoiner j = new StringJoiner(",", "[", "]");
        for (String k : new TreeSet<>(p.keySet())) j.add(k + "=" + p.getStringOr(k, ""));
        return id + j;
    }
    static BlockState state(Tag t) {
        return CACHE.computeIfAbsent(key(t), s -> {
            try { return BlockStateParser.parseForBlock(BuiltInRegistries.BLOCK, s, false).blockState(); }
            catch (Exception e) { throw new RuntimeException("bad state " + s, e); }
        });
    }
    static boolean full(Tag t) {
        return FULL.computeIfAbsent(key(t), s -> state(t).isCollisionShapeFullBlock(EmptyBlockGetter.INSTANCE, BlockPos.ZERO));
    }
    static boolean wet(Tag t) {
        BlockState st = state(t); String id = key(t);
        if (id.startsWith("minecraft:water") || id.startsWith("minecraft:bubble_column")) return true;
        if (id.startsWith("minecraft:kelp") || id.contains("seagrass")) return true;
        return st.hasProperty(BlockStateProperties.WATERLOGGED) && st.getValue(BlockStateProperties.WATERLOGGED);
    }
    static final Tag AIR = StringTag.valueOf("minecraft:air");
    /** a section without block states (light only, saved by the server) is air */
    static Tag[] decode(CompoundTag sec) {
        if (sec.getCompoundOrEmpty("block_states").getListOrEmpty("palette").isEmpty()) { Tag[] t = new Tag[4096]; Arrays.fill(t, AIR); return t; }
        return BlockWriter.decode(sec);
    }
    /** the sections of a chunk by their y index from MINY (missing ones are air) */
    static Tag[][] sections(CompoundTag ch) {
        Tag[][] out = new Tag[(MAXY - MINY + 1) / 16][];
        for (Tag t : ch.getListOrEmpty("sections")) { CompoundTag c = (CompoundTag) t; int i = c.getByteOr("Y", (byte) 0) - (MINY >> 4); if (i >= 0 && i < out.length) out[i] = decode(c); }
        for (int i = 0; i < out.length; i++) if (out[i] == null) { out[i] = new Tag[4096]; Arrays.fill(out[i], AIR); }
        return out;
    }
    static Tag barrier(boolean w) {
        CompoundTag c = new CompoundTag(); c.putString("id", "minecraft:barrier"); CompoundTag p = new CompoundTag(); p.putString("waterlogged", w ? "true" : "false"); c.put("properties", p); return c;
    }

    record Line(String id, String axis, int a, int lo, int hi, List<int[]> gaps) {
        boolean inGap(int along) { for (int[] g : gaps) if (along >= g[0] && along <= g[1]) return true; return false; }
        int x(int along) { return axis.equals("x") ? a : along; }
        int z(int along) { return axis.equals("x") ? along : a; }
    }
    static List<Line> lines(Path json, Set<String> only) throws Exception {
        String s = Files.readString(json); List<Line> out = new ArrayList<>();
        // tiny parser for the generator's own JSON: {"borders": [{"id":..,"axis":..,"a":..,"lo":..,"hi":..,"gaps":[[a,b],..],"test":..}, ..]}
        for (String obj : s.split("\\{\\s*\"id\"")) {
            if (!obj.contains("\"axis\"")) continue;
            String id = obj.split("\"")[1];
            String axis = obj.replaceAll("(?s).*\"axis\":\\s*\"(\\w)\".*", "$1");
            int a = Integer.parseInt(obj.replaceAll("(?s).*\"a\":\\s*(-?\\d+).*", "$1"));
            int lo = Integer.parseInt(obj.replaceAll("(?s).*\"lo\":\\s*(-?\\d+).*", "$1"));
            int hi = Integer.parseInt(obj.replaceAll("(?s).*\"hi\":\\s*(-?\\d+).*", "$1"));
            String g = obj.replaceAll("(?s).*\"gaps\":\\s*\\[(.*?)\\]\\s*,\\s*\"test\".*", "$1");
            List<int[]> gaps = new ArrayList<>();
            java.util.regex.Matcher m = java.util.regex.Pattern.compile("\\[\\s*(-?\\d+)\\s*,\\s*(-?\\d+)\\s*\\]").matcher(g);
            while (m.find()) gaps.add(new int[]{Integer.parseInt(m.group(1)), Integer.parseInt(m.group(2))});
            if (only.isEmpty() || only.contains(id)) out.add(new Line(id, axis, a, lo, hi, gaps));
        }
        return out;
    }

    public static void main(String[] a) throws Exception {
        SharedConstants.tryDetectVersion(); Bootstrap.bootStrap();
        Path world = Paths.get(a[1]);
        switch (a[0]) {
            case "apply" -> apply(world, lines(Paths.get(a[2]), new HashSet<>(Arrays.asList(Arrays.copyOfRange(a, 3, a.length)))));
            case "holes" -> holes(world, lines(Paths.get(a[2]), new HashSet<>(Arrays.asList(Arrays.copyOfRange(a, 4, a.length)))), Paths.get(a[3]));
            case "wallmap" -> wallmap(world, Integer.parseInt(a[2]), Integer.parseInt(a[3]), Integer.parseInt(a[4]), Integer.parseInt(a[5]), Paths.get(a[6]));
            default -> throw new IllegalArgumentException(a[0]);
        }
    }
    static RegionFileStorage open(Path world) {
        return new RegionFileStorage(new RegionStorageInfo("world", Level.OVERWORLD, "chunk"), world.resolve("dimensions/minecraft/overworld/region"), false);
    }
    /** chunk key -> list of (x, z) plane columns of all lines inside that chunk */
    static Map<Long, List<int[]>> columns(List<Line> ls) {
        Map<Long, List<int[]>> m = new TreeMap<>();
        for (Line l : ls) for (int t = l.lo; t <= l.hi; t++) {
            if (l.inGap(t)) continue;
            int x = l.x(t), z = l.z(t);
            m.computeIfAbsent((((long) Math.floorDiv(x, 16)) << 32) | (Math.floorDiv(z, 16) & 0xffffffffL), k -> new ArrayList<>()).add(new int[]{x, z});
        }
        return m;
    }
    static ChunkPos cp(long k) { return new ChunkPos((int) (k >> 32), (int) k); }

    static void apply(Path world, List<Line> ls) throws Exception {
        long t0 = System.currentTimeMillis(); int set = 0, chunks = 0; List<String> missing = new ArrayList<>();
        try (RegionFileStorage st = open(world)) {
            for (var e : columns(ls).entrySet()) {
                ChunkPos c = cp(e.getKey()); CompoundTag ch = st.read(c);
                // only finished chunks: a proto-chunk would still get caves carved through the plane by the generator
                if (ch == null || !ch.getStringOr("Status", "").endsWith("full")) { missing.add(c.x() + "," + c.z()); continue; }
                ListTag secs = ch.getListOrEmpty("sections"); Map<Integer, Integer> yIdx = new HashMap<>(); Tag[][] blocks = new Tag[secs.size()][];
                for (int i = 0; i < secs.size(); i++) yIdx.put((int) secs.getCompoundOrEmpty(i).getByteOr("Y", (byte) 0), i);
                Set<String> cleared = new HashSet<>(); boolean dirty = false;
                for (int[] xz : e.getValue()) for (int y = MINY; y <= MAXY; y++) {
                    Integer si = yIdx.get(Math.floorDiv(y, 16)); if (si == null) continue;
                    if (blocks[si] == null) { if (secs.getCompoundOrEmpty(si).getCompoundOrEmpty("block_states").getListOrEmpty("palette").isEmpty()) continue; blocks[si] = BlockWriter.decode(secs.getCompoundOrEmpty(si)); }
                    int idx = ((y & 15) << 8) | ((xz[1] & 15) << 4) | (xz[0] & 15); Tag t = blocks[si][idx];
                    if (full(t)) continue;
                    blocks[si][idx] = barrier(wet(t)); set++; dirty = true; cleared.add(xz[0] + "," + y + "," + xz[1]);
                }
                if (!dirty) continue;
                for (int i = 0; i < blocks.length; i++) if (blocks[i] != null) BlockWriter.encode(secs.getCompoundOrEmpty(i), blocks[i]);
                ListTag bel = new ListTag();
                for (Tag t : ch.getListOrEmpty("block_entities")) { CompoundTag b = (CompoundTag) t; if (!cleared.contains(b.getIntOr("x", 0) + "," + b.getIntOr("y", 0) + "," + b.getIntOr("z", 0))) bel.add(b); }
                ch.put("block_entities", bel); ch.putBoolean("isLightOn", false); ch.remove("Heightmaps"); st.write(c, ch); chunks++;
            }
        }
        System.out.printf("borders apply: %d lines, %d barrier blocks set, %d chunks written, %d chunks missing, %.1fs%n", ls.size(), set, chunks, missing.size(), (System.currentTimeMillis() - t0) / 1000.0);
        if (!missing.isEmpty()) System.out.println("MISSING chunks (not generated, skipped): " + String.join(" ", missing));
    }

    static void holes(Path world, List<Line> ls, Path out) throws Exception {
        StringBuilder sb = new StringBuilder(); List<String> missing = new ArrayList<>();
        try (RegionFileStorage st = open(world)) {
            Map<Long, Tag[][]> cache = new HashMap<>();
            for (Line l : ls) {
                int n = 0; StringBuilder hs = new StringBuilder();
                for (int t = l.lo; t <= l.hi; t++) {
                    if (l.inGap(t)) continue;
                    int x = l.x(t), z = l.z(t); long k = (((long) Math.floorDiv(x, 16)) << 32) | (Math.floorDiv(z, 16) & 0xffffffffL);
                    Tag[][] secs = cache.get(k);
                    if (secs == null) { CompoundTag ch = st.read(cp(k)); if (ch == null || !ch.getStringOr("Status", "").endsWith("full")) { secs = new Tag[0][]; missing.add(l.id + ":" + cp(k).x() + "," + cp(k).z()); } else { secs = sections(ch); } cache.put(k, secs); }
                    if (secs.length == 0) continue;
                    int lowY = Integer.MIN_VALUE, cnt = 0;
                    for (int y = MINY; y <= MAXY; y++) { Tag tg = secs[(y - MINY) >> 4][(((y - MINY) & 15) << 8) | ((z & 15) << 4) | (x & 15)]; if (!full(tg)) { cnt++; if (lowY == Integer.MIN_VALUE) lowY = y; } }
                    if (cnt > 0) { n++; if (n <= 50) hs.append(String.format(" %d,%d(y%d,%d)", x, z, lowY, cnt)); }
                }
                sb.append(l.id).append(' ').append(n).append(hs).append('\n');
            }
        }
        for (String m : new TreeSet<>(missing)) sb.append("missing ").append(m).append('\n');
        Files.writeString(out, sb.toString()); System.out.print(sb);
    }

    static void wallmap(Path world, int x1, int z1, int x2, int z2, Path out) throws Exception {
        StringBuilder sb = new StringBuilder(); Map<Long, Tag[][]> cache = new HashMap<>();
        sb.append(x1).append(' ').append(z1).append(' ').append(x2).append(' ').append(z2).append('\n');
        try (RegionFileStorage st = open(world)) {
            for (int z = z1; z <= z2; z++) {
                for (int x = x1; x <= x2; x++) {
                    long k = (((long) Math.floorDiv(x, 16)) << 32) | (Math.floorDiv(z, 16) & 0xffffffffL);
                    Tag[][] secs = cache.get(k);
                    if (secs == null) { CompoundTag ch = st.read(cp(k)); if (ch == null || !ch.getStringOr("Status", "").endsWith("full")) secs = new Tag[0][]; else secs = sections(ch); cache.put(k, secs); }
                    char c = '?';
                    if (secs.length > 0) { c = '1'; for (int y = MINY; y <= MAXY; y++) { if (!full(secs[(y - MINY) >> 4][(((y - MINY) & 15) << 8) | ((z & 15) << 4) | (x & 15)])) { c = '0'; break; } } }
                    sb.append(c);
                }
                sb.append('\n');
            }
        }
        Files.writeString(out, sb.toString()); System.out.println("wallmap written: " + out);
    }
}
