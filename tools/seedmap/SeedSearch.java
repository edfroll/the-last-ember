import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.LongStream;

import net.minecraft.SharedConstants;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.registries.Registries;
import net.minecraft.data.registries.VanillaRegistries;
import net.minecraft.server.Bootstrap;
import net.minecraft.world.level.LevelHeightAccessor;
import net.minecraft.world.level.biome.BiomeResolver;
import net.minecraft.world.level.biome.BiomeSource;
import net.minecraft.world.level.biome.MultiNoiseBiomeSource;
import net.minecraft.world.level.biome.MultiNoiseBiomeSourceParameterList;
import net.minecraft.world.level.biome.MultiNoiseBiomeSourceParameterLists;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.NoiseBasedChunkGenerator;
import net.minecraft.world.level.levelgen.NoiseGeneratorSettings;
import net.minecraft.world.level.levelgen.RandomState;

/**
 * Seed scoring (T-002). Evaluates the HQ criteria for many seeds on a regular grid, writes one CSV line per seed.
 * Usage: SeedSearch <out.csv> <stride> <from> <count>            (consecutive seeds)
 *        SeedSearch <out.csv> <stride> list <seed,seed,...>
 * Hard criteria first on the +-650 box (cheap), full scoring only for survivors.
 * Heights: "top" = Y of the top block (first free Y minus 1). Water cell: first free Y <= sea level.
 */
public class SeedSearch {
    static final int SIZE = 3200, HALF = SIZE / 2;
    static final Set<String> COLD = names("snowy_plains ice_spikes snowy_taiga taiga old_growth_pine_taiga old_growth_spruce_taiga grove snowy_slopes jagged_peaks frozen_peaks stony_peaks snowy_beach frozen_river frozen_ocean deep_frozen_ocean");
    static final Set<String> DRY = names("desert badlands eroded_badlands wooded_badlands savanna savanna_plateau windswept_savanna");
    static final Set<String> OCEAN = names("ocean deep_ocean cold_ocean deep_cold_ocean lukewarm_ocean deep_lukewarm_ocean warm_ocean frozen_ocean deep_frozen_ocean");
    static Set<String> names(String s) { Set<String> r = new HashSet<>(); for (String n : s.split(" ")) r.add("minecraft:" + n); return r; }

    static NoiseBasedChunkGenerator gen; static BiomeSource biomeSource; static LevelHeightAccessor lha;
    static NoiseGeneratorSettings settings; static int sea;

    public static void main(String[] a) throws Exception {
        Path out = Paths.get(a[0]); int stride = Integer.parseInt(a[1]);
        SharedConstants.tryDetectVersion(); Bootstrap.bootStrap();
        HolderLookup.Provider lookup = VanillaRegistries.createWorldLookup();
        Holder<NoiseGeneratorSettings> hs = lookup.lookupOrThrow(Registries.NOISE_SETTINGS).getOrThrow(NoiseGeneratorSettings.OVERWORLD);
        Holder<MultiNoiseBiomeSourceParameterList> preset = lookup.lookupOrThrow(Registries.MULTI_NOISE_BIOME_SOURCE_PARAMETER_LIST).getOrThrow(MultiNoiseBiomeSourceParameterLists.OVERWORLD);
        settings = hs.value(); sea = settings.seaLevel();
        biomeSource = MultiNoiseBiomeSource.createFromPreset(preset);
        gen = new NoiseBasedChunkGenerator(biomeSource, hs);
        lha = LevelHeightAccessor.create(settings.noiseSettings().minY(), settings.noiseSettings().height());
        var noises = lookup.lookupOrThrow(Registries.NOISE);
        long[] seeds;
        if (a[2].equals("list")) seeds = Arrays.stream(a[3].split(",")).mapToLong(Long::parseLong).toArray();
        else { long from = Long.parseLong(a[2]); int n = Integer.parseInt(a[3]); seeds = LongStream.range(from, from + n).toArray(); }
        boolean header = !Files.exists(out);
        try (PrintWriter w = new PrintWriter(new FileWriter(out.toFile(), true))) {
            if (header) w.println("seed,pass,score,hub,dol,north_cold,south_dry,west_sea,east_land,north_peaks,water_box,center_land,hub_y,hub_prom,ring_land,ring_cliff,ring_inrange,n_cold,s_dry,w_ocean,e_land,peaks_frac");
            AtomicInteger done = new AtomicInteger(); long t0 = System.currentTimeMillis();
            Arrays.stream(seeds).parallel().forEach(seed -> {
                String line;
                try { line = score(seed, stride, noises); } catch (Throwable t) { t.printStackTrace(); return; }
                synchronized (w) { w.println(line); w.flush(); }
                int d = done.incrementAndGet();
                if (d % 50 == 0) System.err.printf("%d/%d seeds, %.0fs%n", d, seeds.length, (System.currentTimeMillis() - t0) / 1000.0);
            });
        }
    }

    // ---- per-seed grid with lazy cells ----
    static class Grid {
        final RandomState rs; final BiomeResolver res; final int stride, n; final int[] h; final String[] b;
        Grid(long seed, int stride, net.minecraft.core.HolderGetter<net.minecraft.world.level.levelgen.synth.NormalNoise> noises) {
            rs = RandomState.create(noises, seed, settings); res = biomeSource.createUncachedResolver(rs); this.stride = stride; n = SIZE / stride;
            h = new int[n * n]; Arrays.fill(h, Integer.MIN_VALUE); b = new String[n * n];
        }
        int cx(int i) { return -HALF + i * stride + stride / 2; }
        int idx(double x) { return (int) Math.floor((x + HALF) / stride); }
        int height(int xi, int zi) {
            int k = zi * n + xi;
            if (h[k] == Integer.MIN_VALUE) h[k] = gen.getBaseHeight(cx(xi), cx(zi), Heightmap.Types.WORLD_SURFACE_WG, lha, rs);
            return h[k];
        }
        String biome(int xi, int zi) {
            int k = zi * n + xi;
            if (b[k] == null) { int y = Math.max(height(xi, zi) - 1, sea - 8); b[k] = res.getNoiseBiome(cx(xi) >> 2, y >> 2, cx(zi) >> 2).unwrapKey().get().identifier().toString(); }
            return b[k];
        }
        boolean water(int xi, int zi) { return height(xi, zi) <= sea; }
    }

    static double clamp(double v) { return Math.max(0, Math.min(1, v)); }

    static String score(long seed, int stride, net.minecraft.core.HolderGetter<net.minecraft.world.level.levelgen.synth.NormalNoise> noises) {
        Grid g = new Grid(seed, stride, noises); int n = g.n;
        // --- cheap prefilter: every 2nd cell of the +-650 box; reject clearly oceanic seeds (margin over the 10% limit)
        int lo = g.idx(-650), hi = g.idx(650);
        { int w0 = 0, t0 = 0; for (int zi = lo; zi <= hi; zi += 2) for (int xi = lo; xi <= hi; xi += 2) { t0++; if (g.water(xi, zi)) w0++; }
          if (w0 / (double) t0 > 0.22 || g.water(g.idx(0), g.idx(0))) return String.format(Locale.ROOT, "%d,0,0,0,0,0,0,0,0,0,%.3f,%d,0,0,0,0,0,0,0,0,0,0", seed, w0 / (double) t0, 0); }
        // --- hard criteria on the +-650 box
        int water = 0, tot = 0;
        for (int zi = lo; zi <= hi; zi++) for (int xi = lo; xi <= hi; xi++) { tot++; if (g.water(xi, zi)) water++; }
        double waterBox = water / (double) tot; int c = g.idx(0);
        boolean centerLand = !g.water(c, c);
        boolean pass = waterBox < 0.10 && centerLand;
        if (!pass) return String.format(Locale.ROOT, "%d,0,0,0,0,0,0,0,0,0,%.3f,%d,0,0,0,0,0,0,0,0,0,0", seed, waterBox, centerLand ? 1 : 0);

        // 1. hub hill
        double ymax = -999, sum = 0; int cnt = 0;
        for (int zi = 0; zi < n; zi++) for (int xi = 0; xi < n; xi++) {
            double dx = g.cx(xi), dz = g.cx(zi), r = Math.hypot(dx, dz);
            if (r <= 150) { int top = g.height(xi, zi) - 1; sum += top; cnt++; if (r <= 60 + stride / 2.0) ymax = Math.max(ymax, top); }
        }
        double prom = ymax - sum / cnt;
        double dist = ymax < 85 ? 85 - ymax : ymax > 100 ? ymax - 100 : 0;
        double hub = 20 * (0.5 * clamp(1 - dist / 15) + 0.5 * clamp(prom / 12));

        // 2. dol ring 200..650: land fraction, cliffs, height range
        int rt = 0, rl = 0, cliff = 0, inr = 0; int cl = (int) (15.0 * stride / 8);
        for (int zi = lo; zi <= hi; zi++) for (int xi = lo; xi <= hi; xi++) {
            double r = Math.hypot(g.cx(xi), g.cx(zi)); if (r < 200 || r > 650) continue;
            rt++; if (g.water(xi, zi)) continue; rl++;
            int top = g.height(xi, zi) - 1; if (top >= 64 && top <= 100) inr++;
            int[][] nb = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}}; boolean cf = false;
            for (int[] d : nb) { int x2 = xi + d[0], z2 = zi + d[1]; if (x2 >= 0 && z2 >= 0 && x2 < n && z2 < n && Math.abs(g.height(x2, z2) - g.height(xi, zi)) > cl) cf = true; }
            if (cf) cliff++;
        }
        double ringLand = rl / (double) rt, cliffFrac = rl == 0 ? 1 : cliff / (double) rl, inrFrac = rl == 0 ? 0 : inr / (double) rl;
        double dol = 20 * (0.5 * clamp((ringLand - 0.5) / 0.4) + 0.25 * (1 - clamp(cliffFrac / 0.05)) + 0.25 * inrFrac);

        // 3..7 regions
        int nT = 0, nC = 0, sT = 0, sD = 0, wT = 0, wO = 0, eT = 0, eL = 0, pT = 0, pH = 0;
        int zN = g.idx(-850), zS = g.idx(650), xW = g.idx(-1250), xE = g.idx(650);
        for (int zi = 0; zi < n; zi++) for (int xi = 0; xi < n; xi++) {
            double x = g.cx(xi), z = g.cx(zi);
            if (z < -850) { nT++; if (COLD.contains(g.biome(xi, zi))) nC++; }
            if (z > 650) { sT++; if (DRY.contains(g.biome(xi, zi))) sD++; }
            if (x < -1250) { wT++; if (g.water(xi, zi)) wO++; }
            if (x > 650) { eT++; if (!g.water(xi, zi)) eL++; }
            if (z >= -900 && z <= -800 && Math.abs(x) > 900) { pT++; if (g.height(xi, zi) - 1 > 120) pH++; }
        }
        double nCold = nC / (double) nT, sDry = sD / (double) sT, wSea = wO / (double) wT, eLand = eL / (double) eT, pk = pH / (double) pT;
        double s3 = 15 * clamp(nCold / 0.7), s4 = 15 * clamp(sDry / 0.7), s5 = 10 * clamp(wSea / 0.7), s6 = 10 * clamp(eLand / 0.9), s7 = 10 * clamp(pk / 0.5);
        double total = hub + dol + s3 + s4 + s5 + s6 + s7;
        return String.format(Locale.ROOT, "%d,1,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.3f,1,%.0f,%.1f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f",
            seed, total, hub, dol, s3, s4, s5, s6, s7, waterBox, ymax, prom, ringLand, cliffFrac, inrFrac, nCold, sDry, wSea, eLand, pk);
    }
}
