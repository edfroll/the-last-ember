# generated: as the holder of the valid key thread_labyrinth: remembered as the last one who held it
scoreboard players set #kh le.alt 1
execute unless entity @s[tag=le.kh_thread_labyrinth] run function last_ember:altar/gen/khn_thread_labyrinth
data modify storage last_ember:keys k.thread_labyrinth.it set value 0b
data modify storage last_ember:keys k.thread_labyrinth.got set value 1b
data modify storage last_ember:keys k.thread_labyrinth.pend set value 0b
