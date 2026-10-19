import com.google.gson.*;
import java.awt.image.BufferedImage;
import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.stream.IntStream;
import javax.imageio.ImageIO;

import net.minecraft.SharedConstants;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.registries.Registries;
import net.minecraft.data.registries.VanillaRegistries;
import net.minecraft.server.Bootstrap;
import net.minecraft.world.level.LevelHeightAccessor;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.biome.BiomeResolver;
import net.minecraft.world.level.biome.BiomeSource;
import net.minecraft.world.level.biome.MultiNoiseBiomeSource;
import net.minecraft.world.level.biome.MultiNoiseBiomeSourceParameterList;
import net.minecraft.world.level.biome.MultiNoiseBiomeSourceParameterLists;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.NoiseBasedChunkGenerator;
import net.minecraft.world.level.levelgen.NoiseGeneratorSettings;
import net.minecraft.world.level.levelgen.RandomState;
import net.minecraft.world.level.levelgen.synth.NormalNoise;

/**
 * Headless world sampler: no server, no chunks. Evaluates vanilla terrain noise + biome source for a seed
 * on a regular grid around (0,0) and writes top-down PNG maps (height, biomes) and a JSON grid.
 * Usage: SeedMap <outDir> <size> <stride> <seed> [seed...]     (size/stride in blocks)
 */
public class SeedMap {
    static final Map<String, Integer> COLORS = new HashMap<>();
    static {
        String[] t = {
            "ocean 0000a0", "deep_ocean 000070", "cold_ocean 202070", "deep_cold_ocean 181850", "lukewarm_ocean 0000ac",
            "deep_lukewarm_ocean 000090", "warm_ocean 0000ac", "frozen_ocean 7070d6", "deep_frozen_ocean 404090",
            "river 3030ff", "frozen_river a0a0ff", "beach faf090", "snowy_beach faf0c0", "stony_shore a2a284",
            "plains 8db360", "sunflower_plains b5db88", "snowy_plains ffffff", "ice_spikes b4dcdc",
            "desert fa9418", "badlands d94515", "eroded_badlands ff6d3d", "wooded_badlands b09765",
            "savanna bdb25f", "savanna_plateau a79d64", "windswept_savanna e5da87",
            "forest 056621", "flower_forest 2d8e49", "birch_forest 307444", "old_growth_birch_forest 589c6c",
            "dark_forest 40511a", "pale_garden a09aa0", "cherry_grove f7b2d8", "meadow 83bb6d", "grove 88bb67",
            "taiga 0b6659", "snowy_taiga 31554a", "old_growth_pine_taiga 596651", "old_growth_spruce_taiga 818e79",
            "jungle 537b09", "sparse_jungle 628b17", "bamboo_jungle 768e14", "swamp 07f9b2", "mangrove_swamp 67352b",
            "mushroom_fields ff00ff", "windswept_hills 606060", "windswept_forest 22551c", "windswept_gravelly_hills 789878",
            "snowy_slopes c4c4d4", "frozen_peaks a0a0c0", "jagged_peaks d0d0e0", "stony_peaks 827e7a",
            "dripstone_caves 4e3f2e", "lush_caves 7ac64c", "deep_dark 0a2a30"
        };
        for (String s : t) { String[] p = s.split(" "); COLORS.put("minecraft:" + p[0], Integer.parseInt(p[1], 16)); }
    }

    static int colorOf(String name) {
        Integer c = COLORS.get(name);
        if (c != null) return c;
        int h = name.hashCode();
        return 0x404040 | ((h & 0x7f7f7f));
    }

    public static void main(String[] a) throws Exception {
        Path out = Paths.get(a[0]);
        int size = Integer.parseInt(a[1]), stride = Integer.parseInt(a[2]);
        Files.createDirectories(out);
        SharedConstants.tryDetectVersion();
        Bootstrap.bootStrap();
        HolderLookup.Provider lookup = VanillaRegistries.createWorldLookup();
        Holder<NoiseGeneratorSettings> settings = lookup.lookupOrThrow(Registries.NOISE_SETTINGS).getOrThrow(NoiseGeneratorSettings.OVERWORLD);
        Holder<MultiNoiseBiomeSourceParameterList> preset = lookup.lookupOrThrow(Registries.MULTI_NOISE_BIOME_SOURCE_PARAMETER_LIST).getOrThrow(MultiNoiseBiomeSourceParameterLists.OVERWORLD);
        var noises = lookup.lookupOrThrow(Registries.NOISE);
        BiomeSource biomeSource = MultiNoiseBiomeSource.createFromPreset(preset);
        NoiseBasedChunkGenerator gen = new NoiseBasedChunkGenerator(biomeSource, settings);
        LevelHeightAccessor lha = LevelHeightAccessor.create(settings.value().noiseSettings().minY(), settings.value().noiseSettings().height());
        int sea = settings.value().seaLevel();
        int n = size / stride, half = size / 2;
        for (int i = 3; i < a.length; i++) {
            long seed = Long.parseLong(a[i]);
            long t0 = System.currentTimeMillis();
            RandomState rs = RandomState.create(noises, seed, settings.value());
            BiomeResolver res = biomeSource.createUncachedResolver(rs);
            int[] surf = new int[n * n], floor = new int[n * n];
            String[] biome = new String[n * n];
            IntStream.range(0, n).parallel().forEach(zi -> {
                for (int xi = 0; xi < n; xi++) {
                    int x = -half + xi * stride + stride / 2, z = -half + zi * stride + stride / 2;
                    int s = gen.getBaseHeight(x, z, Heightmap.Types.WORLD_SURFACE_WG, lha, rs);
                    int f = s;
                    if (s <= sea) { // water column: walk down the base column to the sea floor
                        var col = gen.getBaseColumn(x, z, lha, rs);
                        f = s;
                        while (f > lha.getMinY() && !col.getBlock(f - 1).getFluidState().isEmpty()) f--;
                        f = Math.max(lha.getMinY(), f - 1);
                    }
                    surf[zi * n + xi] = s; floor[zi * n + xi] = f;
                    int y = Math.max(f, sea - 8);
                    biome[zi * n + xi] = res.getNoiseBiome(x >> 2, y >> 2, z >> 2).unwrapKey().get().identifier().toString();
                }
            });
            render(out, seed, n, stride, half, sea, surf, floor, biome);
            System.out.printf("seed %d done in %.1fs%n", seed, (System.currentTimeMillis() - t0) / 1000.0);
        }
    }

    static void render(Path out, long seed, int n, int stride, int half, int sea, int[] surf, int[] floor, String[] biome) throws IOException {
        BufferedImage hi = new BufferedImage(n, n, BufferedImage.TYPE_INT_RGB), bi = new BufferedImage(n, n, BufferedImage.TYPE_INT_RGB);
        for (int z = 0; z < n; z++) for (int x = 0; x < n; x++) {
            int i = z * n + x, h = floor[i];
            // hillshade from NW light
            int hx = floor[z * n + Math.min(n - 1, x + 1)] - floor[z * n + Math.max(0, x - 1)];
            int hz = floor[Math.min(n - 1, z + 1) * n + x] - floor[Math.max(0, z - 1) * n + x];
            double shade = Math.max(0.55, Math.min(1.35, 1.0 - (hx + hz) * 0.02 * (8.0 / stride) * 0.5));
            int rgb;
            if (surf[i] <= sea && floor[i] < sea) { // water column
                double d = Math.min(1.0, (sea - floor[i]) / 60.0);
                rgb = mix(0x4a8bd0, 0x0a1a50, d);
            } else {
                double t = Math.max(0, Math.min(1, (h - sea) / 220.0));
                rgb = t < 0.5 ? mix(0x3c8c3c, 0xb9a26a, t * 2) : mix(0xb9a26a, 0xffffff, (t - 0.5) * 2);
                rgb = scale(rgb, shade);
            }
            hi.setRGB(x, z, grid(rgb, x, z, n, stride, half));
            bi.setRGB(x, z, grid(colorOf(biome[i]), x, z, n, stride, half));
        }
        hi = up(hi, 2); bi = up(bi, 2);
        ImageIO.write(hi, "png", out.resolve("seed_" + seed + "_height.png").toFile());
        ImageIO.write(bi, "png", out.resolve("seed_" + seed + "_biomes.png").toFile());
        // JSON grid for scoring scripts
        Map<String, Integer> pal = new LinkedHashMap<>();
        int[] idx = new int[n * n];
        for (int i = 0; i < idx.length; i++) idx[i] = pal.computeIfAbsent(biome[i], k -> pal.size());
        JsonObject o = new JsonObject();
        o.addProperty("seed", seed); o.addProperty("size", n * stride); o.addProperty("stride", stride);
        o.addProperty("origin_x", -half); o.addProperty("origin_z", -half); o.addProperty("sea_level", sea); o.addProperty("n", n);
        o.add("biomes", new Gson().toJsonTree(new ArrayList<>(pal.keySet())));
        o.add("biome_index", new Gson().toJsonTree(idx));
        // getBaseHeight returns the first free Y above the terrain; export the Y of the top block (minus 1).
        // height_surface: top block incl. water (ocean = sea_level-1); height_floor: top solid block (ocean floor under water).
        o.add("height_floor", new Gson().toJsonTree(Arrays.stream(floor).map(v -> v - 1).toArray()));
        o.add("height_surface", new Gson().toJsonTree(Arrays.stream(surf).map(v -> v - 1).toArray()));
        Map<String, Double> pct = new TreeMap<>();
        for (String b : biome) pct.merge(b.replace("minecraft:", ""), 100.0 / biome.length, Double::sum);
        int ocean = 0; for (int i = 0; i < surf.length; i++) if (surf[i] <= sea) ocean++;
        System.out.printf("  seed %d: ocean %.0f%%, max height %d; biomes: %s%n", seed, 100.0 * ocean / surf.length, Arrays.stream(surf).max().getAsInt(),
            pct.entrySet().stream().sorted((x, y) -> Double.compare(y.getValue(), x.getValue())).limit(8).map(e -> String.format("%s %.0f%%", e.getKey(), e.getValue())).toList());
        try (Writer w = Files.newBufferedWriter(out.resolve("seed_" + seed + "_grid.json"))) { w.write(o.toString()); }
    }

    static BufferedImage up(BufferedImage src, int k) {
        BufferedImage o = new BufferedImage(src.getWidth() * k, src.getHeight() * k, BufferedImage.TYPE_INT_RGB);
        for (int y = 0; y < o.getHeight(); y++) for (int x = 0; x < o.getWidth(); x++) o.setRGB(x, y, src.getRGB(x / k, y / k));
        return o;
    }

    // thin grid line every 400 blocks, stronger every 800, crosshair at origin
    static int grid(int rgb, int x, int z, int n, int stride, int half) {
        int wx = -half + x * stride, wz = -half + z * stride;
        boolean l400 = Math.floorMod(wx, 400) < stride || Math.floorMod(wz, 400) < stride;
        boolean l800 = Math.floorMod(wx, 800) < stride || Math.floorMod(wz, 800) < stride;
        boolean origin = (Math.abs(wx) < stride && Math.abs(wz) < 64) || (Math.abs(wz) < stride && Math.abs(wx) < 64);
        if (origin) return 0xff0000;
        if (l800) return mix(rgb, 0x000000, 0.35);
        if (l400) return mix(rgb, 0x000000, 0.12);
        return rgb;
    }
    static int mix(int a, int b, double t) {
        int r = (int) (((a >> 16) & 255) * (1 - t) + ((b >> 16) & 255) * t), g = (int) (((a >> 8) & 255) * (1 - t) + ((b >> 8) & 255) * t), bl = (int) ((a & 255) * (1 - t) + (b & 255) * t);
        return (r << 16) | (g << 8) | bl;
    }
    static int scale(int c, double s) {
        int r = Math.min(255, (int) (((c >> 16) & 255) * s)), g = Math.min(255, (int) (((c >> 8) & 255) * s)), b = Math.min(255, (int) ((c & 255) * s));
        return (r << 16) | (g << 8) | b;
    }
}
