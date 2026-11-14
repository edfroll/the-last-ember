# altar/reset {chapter:1} (test/admin): the world back as before the end of chapter I. The Circle (poses, core, candles) follows the altar
# by itself (weepers/sync: done = 0b -> the templates "before"); the region R1 un-fades (biomes back, the bonfires that went out burn again);
# the west pass closes again. The respawn points of the players are not touched.
function last_ember:region/gen/unfade_r1
function last_ember:gate/close {id:"west_pass"}
