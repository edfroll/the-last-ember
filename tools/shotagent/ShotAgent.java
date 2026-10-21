import java.io.File;
import java.lang.instrument.Instrumentation;
import java.nio.file.*;
import java.util.List;

import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.world.entity.player.ChatVisiblity;

/**
 * Dev-only Java agent for the LOCAL test client (never shipped with the map). Watches <gameDir>/shot-request.txt;
 * each line "<name> <hud:0|1>" -> saves screenshots/<name>.png from the real render target, then writes shot-done.txt.
 * Needs no OS permissions (no key injection, no screen recording). Launch via tools/client_launch.py.
 */
public class ShotAgent {
    public static void premain(String args, Instrumentation inst) {
        Thread t = new Thread(() -> {
            Path dir = Paths.get(args), req = dir.resolve("shot-request.txt"), done = dir.resolve("shot-done.txt");
            try { Thread.sleep(25000); } catch (InterruptedException e) { return; }  // do not touch Minecraft during startup
            while (true) {
                try {
                    Thread.sleep(200);
                    if (!Files.exists(req)) {
                        // camera must never sit on the death screen: auto-respawn (saved player data may be dead)
                        Minecraft m = Minecraft.getInstance();
                        if (m != null && m.player != null && m.player.isDeadOrDying()) m.execute(() -> { if (m.player != null && m.player.isDeadOrDying()) m.player.respawn(); });
                        continue;
                    }
                    List<String> lines = Files.readAllLines(req);
                    Files.delete(req);
                    Minecraft mc = Minecraft.getInstance();
                    if (mc == null || mc.player == null) { Files.writeString(done, "no-player\n"); continue; }
                    StringBuilder res = new StringBuilder();
                    for (String line : lines) {
                        String[] p = line.trim().split("\\s+");
                        if (p[0].isEmpty()) continue;
                        if (p[0].equals("!fps")) { res.append("fps ").append(mc.getFps()).append('\n'); continue; }  // perf report (T-008)
                        if (p[0].startsWith("!")) { // input actions for tests: !use (right click), !drop (Q), !sneak_on / !sneak_off
                            String act = p[0].substring(1);
                            mc.execute(() -> {
                                if (mc.gui.screen() != null) mc.gui.setScreen(null);
                                switch (act) {
                                    case "use" -> KeyMapping.click(mc.options.keyUse.getDefaultKey());
                                    case "drop" -> KeyMapping.click(mc.options.keyDrop.getDefaultKey());
                                    case "sneak_on" -> KeyMapping.set(mc.options.keyShift.getDefaultKey(), true);
                                    case "sneak_off" -> KeyMapping.set(mc.options.keyShift.getDefaultKey(), false);
                                    default -> {}
                                }
                            });
                            Thread.sleep(150);
                            res.append(p[0]).append(" ok\n");
                            continue;
                        }
                        boolean hud = p.length > 1 && p[1].equals("1");
                        Object lock = new Object();
                        boolean[] ok = {false};
                        Path shots = Paths.get(mc.gameDirectory.getPath(), "screenshots");
                        Files.createDirectories(shots);
                        mc.execute(() -> {
                            if (mc.gui.screen() != null) mc.gui.setScreen(null);  // close pause menu etc.
                            if (!hud) { mc.options.chatVisibility().set(ChatVisiblity.HIDDEN); mc.gui.hud.getChat().clearMessages(false); }  // no chat / "Saved screenshot"
                            boolean wasHidden = mc.gui.hud.isHidden();
                            if (wasHidden == hud) mc.gui.hud.toggle();
                            // capture on a later frame so the HUD state has been rendered
                            mc.execute(() -> mc.execute(() -> {
                                Screenshot.grab(mc, false);  // same path as F2: screenshots/<timestamp>.png, written async
                                if (wasHidden == hud) mc.gui.hud.toggle();
                                synchronized (lock) { ok[0] = true; lock.notifyAll(); }
                            }));
                        });
                        synchronized (lock) { if (!ok[0]) lock.wait(15000); }
                        Path target = shots.resolve(p[0] + ".png");
                        Files.deleteIfExists(target);
                        long end = System.currentTimeMillis() + 8000; Path found = null;
                        while (found == null && System.currentTimeMillis() < end) {
                            Thread.sleep(150);
                            try (var st = Files.list(shots)) {
                                found = st.filter(f -> f.getFileName().toString().matches("\\d{4}-.*\\.png")).max((x, y) -> Long.compare(x.toFile().lastModified(), y.toFile().lastModified())).orElse(null);
                            }
                        }
                        mc.execute(() -> mc.options.chatVisibility().set(ChatVisiblity.FULL));
                        if (found != null) Files.move(found, target, StandardCopyOption.REPLACE_EXISTING); else ok[0] = false;
                        res.append(p[0]).append(ok[0] ? " ok\n" : " timeout\n");
                    }
                    Thread.sleep(500);
                    Files.writeString(done, res.toString());
                } catch (Throwable e) { try { Files.writeString(dir.resolve("shot-done.txt"), "error " + e + "\n"); } catch (Exception ignored) {} }
            }
        }, "shot-agent");
        t.setDaemon(true);
        t.start();
    }
}
