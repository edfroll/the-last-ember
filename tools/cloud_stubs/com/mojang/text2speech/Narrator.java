package com.mojang.text2speech;
/** Cloud stub of Mojang's text2speech (not downloadable in the cloud): the narrator that never speaks. */
public interface Narrator {
    void say(String msg, boolean interrupt, float volume);
    void clear();
    boolean active();
    void destroy();
    static Narrator getNarrator() {
        return new Narrator() {
            public void say(String msg, boolean interrupt, float volume) {}
            public void clear() {}
            public boolean active() { return false; }
            public void destroy() {}
        };
    }
}
