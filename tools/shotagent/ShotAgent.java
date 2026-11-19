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
    static volatile boolean ATTACK = false;
    static volatile long RAPID_END = 0; static volatile int RAPID_MS = 100;   // !use_rapid <ms> [every_ms]: right clicks in a row (T-025 review: the door)
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
                        if (m != null && m.gui.screen() != null && m.gui.screen().getClass().getName().endsWith("PackConfirmScreen")) m.execute(() -> {  // accept the server resource pack
                            try { var sc = m.gui.screen(); var f = net.minecraft.client.gui.screens.ConfirmScreen.class.getDeclaredField("callback"); f.setAccessible(true);
                                  ((it.unimi.dsi.fastutil.booleans.BooleanConsumer) f.get(sc)).accept(true); } catch (Exception ex) { ex.printStackTrace(); }
                        });
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
                                if (mc.gui.screen() != null && !act.startsWith("trade") && !act.startsWith("menu")) { if (mc.player != null && mc.gui.screen() instanceof net.minecraft.client.gui.screens.inventory.AbstractContainerScreen) mc.player.closeContainer(); else mc.gui.setScreen(null); }   // a container is closed properly (the server gets the packet: the items of a trade window come back)
                                switch (act) {
                                    case "use" -> KeyMapping.click(mc.options.keyUse.getDefaultKey());
                                    case "drop" -> KeyMapping.click(mc.options.keyDrop.getDefaultKey());
                                    case "swap" -> KeyMapping.click(mc.options.keySwapOffhand.getDefaultKey());   // F (T-014)
                                    case "trade_sel" -> { if (mc.player != null && mc.player.containerMenu instanceof net.minecraft.world.inventory.MerchantMenu && mc.getConnection() != null) mc.getConnection().send(new net.minecraft.network.protocol.game.ServerboundSelectTradePacket(Integer.parseInt(p.length > 1 ? p[1] : "0"))); }   // T-017: select trade N in the open merchant screen
                                    case "trade_take" -> { if (mc.player != null && mc.player.containerMenu instanceof net.minecraft.world.inventory.MerchantMenu mm) mc.gameMode.handleContainerInput(mm.containerId, 2, 0, net.minecraft.world.inventory.ContainerInput.QUICK_MOVE, mc.player); }   // shift-click the result
                                    case "sneak_on" -> KeyMapping.set(mc.options.keyShift.getDefaultKey(), true);
                                    case "sneak_off" -> KeyMapping.set(mc.options.keyShift.getDefaultKey(), false);
                                    case "fwd_on" -> KeyMapping.set(mc.options.keyUp.getDefaultKey(), true);     // walk bot (T-008)
                                    case "fwd_off" -> KeyMapping.set(mc.options.keyUp.getDefaultKey(), false);
                                    case "use_on" -> KeyMapping.set(mc.options.keyUse.getDefaultKey(), true);    // hold right mouse (shield, bow)
                                    case "use_off" -> KeyMapping.set(mc.options.keyUse.getDefaultKey(), false);
                                    case "jump_on" -> KeyMapping.set(mc.options.keyJump.getDefaultKey(), true);  // jump uses the held state
                                    case "jump_off" -> KeyMapping.set(mc.options.keyJump.getDefaultKey(), false);
                                    case "attack_on" -> { KeyMapping.set(mc.options.keyAttack.getDefaultKey(), true); ATTACK = true; }   // hold left mouse: break a block (T-025); vanilla mines on a held key only with the mouse grabbed (a focused window), so the agent drives the destroy itself (below)
                                    case "use_rapid" -> { RAPID_MS = Math.max(20, Integer.parseInt(p.length > 2 ? p[2] : "100")); RAPID_END = System.currentTimeMillis() + Integer.parseInt(p.length > 1 ? p[1] : "3000"); }
                                    case "menu_qmove" -> { if (mc.player != null && mc.player.containerMenu != null && mc.player.containerMenu.containerId != 0) mc.gameMode.handleContainerInput(mc.player.containerMenu.containerId, Integer.parseInt(p.length > 1 ? p[1] : "0"), 0, net.minecraft.world.inventory.ContainerInput.QUICK_MOVE, mc.player); }   // T-025: shift-click slot N of the open menu (anvil)
                                    case "attack_off" -> { KeyMapping.set(mc.options.keyAttack.getDefaultKey(), false); ATTACK = false; if (mc.gameMode != null) mc.gameMode.stopDestroyBlock(); }
                                    default -> {}
                                }
                            });
                            Thread.sleep(150);
                            res.append(p[0]).append(" ok\n");
                            continue;
                        }
                        boolean hud = p.length > 1 && p[1].equals("1");
                        boolean keep = p.length > 2 && p[2].equals("keep");     // "<name> 1 keep": the open screen (a book, the inventory) stays in the frame
                        Object lock = new Object();
                        boolean[] ok = {false};
                        Path shots = Paths.get(mc.gameDirectory.getPath(), "screenshots");
                        Files.createDirectories(shots);
                        mc.execute(() -> {
                            if (mc.gui.screen() != null && !keep) mc.gui.setScreen(null);  // close pause menu etc.
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
        Thread a = new Thread(() -> {     // the held attack: every 50 ms the block under the crosshair is mined like a held left mouse button
            while (true) {
                try {
                    Thread.sleep(50);
                    if (!ATTACK) continue;
                    Minecraft mc = Minecraft.getInstance();
                    if (mc == null) continue;
                    mc.execute(() -> {
                        if (!ATTACK || mc.player == null || mc.gameMode == null) return;
                        if (mc.hitResult instanceof net.minecraft.world.phys.BlockHitResult bh && bh.getType() == net.minecraft.world.phys.HitResult.Type.BLOCK) {
                            if (!mc.gameMode.isDestroying()) mc.gameMode.startDestroyBlock(bh.getBlockPos(), bh.getDirection());
                            else mc.gameMode.continueDestroyBlock(bh.getBlockPos(), bh.getDirection());
                        }
                    });
                } catch (Throwable e) { }
            }
        }, "shot-agent-attack");
        a.setDaemon(true);
        a.start();
        Thread u = new Thread(() -> {     // rapid right clicks: one click per RAPID_MS until RAPID_END (vanilla uses every queued click of a frame)
            while (true) {
                try {
                    Thread.sleep(RAPID_MS);
                    if (System.currentTimeMillis() >= RAPID_END) continue;
                    Minecraft mc = Minecraft.getInstance();
                    if (mc != null) mc.execute(() -> KeyMapping.click(mc.options.keyUse.getDefaultKey()));
                } catch (Throwable e) { }
            }
        }, "shot-agent-use");
        u.setDaemon(true);
        u.start();
    }
}
