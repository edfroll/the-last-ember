import com.google.gson.*;
import java.io.*;
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
 * Biome painter (T-006): writes biomes into chunk sections (4x4x4 cells) of existing chunks, server STOPPED.
 * Same result as /fillbiome by contours, but with dithered ("mixed") transition bands and no command-volume limit.
 *   BiomePaint <worldDir> <paint.gen.json>
 * Layers are applied in order; a layer's transition band lies INSIDE its contour: probability of repainting a cell rises
 * linearly from 0 at the contour edge to 1 at 'trans' blocks inside (cell-wise noise), so the biome below shows through.
 */
public class BiomePaint {
    static double hash(int x, int z, int salt) {
        long n = x * 374761393L + z * 668265263L + salt * 1442695040888963407L; n = (n ^ (n >>> 13)) * 1274126177L; n ^= n >>> 16;
        return (n & 0xffffff) / (double) 0x1000000;
    }
    static double vnoise(double x, double z, int salt) {
        int xi = (int) Math.floor(x), zi = (int) Math.floor(z); double fx = x - xi, fz = z - zi;
        fx = fx * fx * (3 - 2 * fx); fz = fz * fz * (3 - 2 * fz);
        double a = hash(xi, zi, salt), b = hash(xi + 1, zi, salt), c = hash(xi, zi + 1, salt), d = hash(xi + 1, zi + 1, salt);
        return (a * (1 - fx) + b * fx) * (1 - fz) + (c * (1 - fx) + d * fx) * fz;
    }
    record Layer(String biome, boolean circle, double[] v, double trans, int y1, int y2, int salt) {
        /** signed depth inside the contour in blocks (negative = outside) */
        double depth(double x, double z) {
            if (circle) return v[2] - Math.hypot(x - v[0], z - v[1]);
            return Math.min(Math.min(x - v[0], v[2] + 1 - x), Math.min(z - v[1], v[3] + 1 - z));
        }
        boolean paints(double x, double z) {
            double d = depth(x, z); if (d < 0) return false;
            if (trans <= 0) return true;
            double p = Math.min(1.0, d / trans);
            double n = hash((int) Math.floor(x / 4), (int) Math.floor(z / 4), salt);  // uniform per-cell noise: p == painted fraction
            return n < p;
        }
        int[] bbox() { return circle ? new int[]{(int) (v[0] - v[2]), (int) (v[1] - v[2]), (int) (v[0] + v[2]), (int) (v[1] + v[2])} : new int[]{(int) v[0], (int) v[1], (int) v[2], (int) v[3]}; }
    }

    public static void main(String[] a) throws Exception {
        SharedConstants.tryDetectVersion(); Bootstrap.bootStrap();
        Path dim = Paths.get(a[0]).resolve("dimensions/minecraft/overworld/region");
        JsonObject spec = JsonParser.parseReader(new FileReader(a[1])).getAsJsonObject();
        List<Layer> layers = new ArrayList<>(); int salt = spec.get("seed").getAsInt();
        for (JsonElement e : spec.getAsJsonArray("layers")) {
            JsonObject o = e.getAsJsonObject(); JsonArray v = o.getAsJsonArray("v"); double[] vv = new double[v.size()]; for (int i = 0; i < vv.length; i++) vv[i] = v.get(i).getAsDouble();
            JsonArray y = o.getAsJsonArray("y");
            layers.add(new Layer(o.get("biome").getAsString(), o.get("shape").getAsString().equals("circle"), vv, o.get("trans").getAsDouble(), y.get(0).getAsInt(), y.get(1).getAsInt(), salt + layers.size() * 31));
        }
        int minCx = Integer.MAX_VALUE, minCz = Integer.MAX_VALUE, maxCx = Integer.MIN_VALUE, maxCz = Integer.MIN_VALUE;
        for (Layer l : layers) { int[] b = l.bbox(); minCx = Math.min(minCx, Math.floorDiv(b[0], 16)); minCz = Math.min(minCz, Math.floorDiv(b[1], 16)); maxCx = Math.max(maxCx, Math.floorDiv(b[2], 16)); maxCz = Math.max(maxCz, Math.floorDiv(b[3], 16)); }
        long t0 = System.currentTimeMillis(); int touched = 0, absent = 0; Map<String, Long> cells = new TreeMap<>();
        try (RegionFileStorage st = new RegionFileStorage(new RegionStorageInfo("world", Level.OVERWORLD, "chunk"), dim, false)) {
            for (int cz = minCz; cz <= maxCz; cz++) for (int cx = minCx; cx <= maxCx; cx++) {
                // does any layer touch this chunk?
                boolean any = false; for (Layer l : layers) { int[] b = l.bbox(); if (cx * 16 + 15 >= b[0] && cx * 16 <= b[2] && cz * 16 + 15 >= b[1] && cz * 16 <= b[3]) { any = true; break; } }
                if (!any) continue;
                ChunkPos cp = new ChunkPos(cx, cz); CompoundTag ch = st.read(cp);
                if (ch == null) { absent++; continue; }
                ListTag secs = ch.getListOrEmpty("sections"); ListTag out = new ListTag(); boolean changed = false;
                for (int si = 0; si < secs.size(); si++) {
                    CompoundTag sec = secs.getCompoundOrEmpty(si); int sy = sec.getByteOr("Y", (byte) 0);
                    CompoundTag bio = sec.getCompoundOrEmpty("biomes"); ListTag pal = bio.getListOrEmpty("palette"); long[] data = bio.getLongArray("data").orElse(null);
                    String[] cell = new String[64];
                    int bits = Math.max(1, 32 - Integer.numberOfLeadingZeros(Math.max(1, pal.size() - 1))), per = 64 / bits; long mask = (1L << bits) - 1;
                    for (int i = 0; i < 64; i++) cell[i] = (data == null || pal.size() == 1) ? ((StringTag) pal.get(0)).value() : ((StringTag) pal.get((int) ((data[i / per] >>> ((i % per) * bits)) & mask))).value();
                    boolean sc = false;
                    for (int ly = 0; ly < 4; ly++) for (int lz = 0; lz < 4; lz++) for (int lx = 0; lx < 4; lx++) {
                        double x = cx * 16 + lx * 4 + 2, z = cz * 16 + lz * 4 + 2; int y = sy * 16 + ly * 4 + 2;
                        for (Layer l : layers) if (y >= l.y1 && y <= l.y2 && l.paints(x, z)) { int i = (ly * 4 + lz) * 4 + lx; if (!cell[i].equals(l.biome)) { cell[i] = l.biome; sc = true; } }
                    }
                    if (!sc) { out.add(sec); continue; }
                    changed = true;
                    LinkedHashMap<String, Integer> pm = new LinkedHashMap<>(); ListTag np = new ListTag(); int[] idx = new int[64];
                    for (int i = 0; i < 64; i++) { Integer p = pm.get(cell[i]); if (p == null) { p = pm.size(); pm.put(cell[i], p); np.add(StringTag.valueOf(cell[i])); } idx[i] = p; }
                    CompoundTag nb = new CompoundTag(); nb.put("palette", np);
                    if (np.size() > 1) { int nbits = Math.max(1, 32 - Integer.numberOfLeadingZeros(np.size() - 1)), nper = 64 / nbits; long[] nd = new long[(64 + nper - 1) / nper]; for (int i = 0; i < 64; i++) nd[i / nper] |= ((long) idx[i]) << ((i % nper) * nbits); nb.put("data", new LongArrayTag(nd)); }
                    CompoundTag ns = sec.copy(); ns.put("biomes", nb); out.add(ns);
                }
                if (changed) { ch.put("sections", out); st.write(cp, ch); touched++; }
                for (int si = 0; si < out.size(); si++) { CompoundTag b = out.getCompoundOrEmpty(si).getCompoundOrEmpty("biomes"); ListTag p = b.getListOrEmpty("palette"); for (int i = 0; i < p.size(); i++) cells.merge(((StringTag) p.get(i)).value(), 1L, Long::sum); }
            }
        }
        System.out.printf("paint: %d chunks rewritten, %d chunks absent (not generated, skipped), %.1fs%n", touched, absent, (System.currentTimeMillis() - t0) / 1000.0);
        System.out.println("sections containing each biome (in painted-area chunks): " + cells);
    }
}
