# T-025: at the place found: a creaking of the sensors (invulnerable, persistent; vanilla AI: it freezes under a look), dust and a creak;
# it crumbles after 60 s (le.gdt), when nobody is near the garden or when the garden falls asleep
summon minecraft:creaking ~ ~ ~ {Tags:["le.garden_cr","le.gcnew","le.noelite","le.keep"],Invulnerable:1b,PersistenceRequired:1b}
scoreboard players operation @e[type=minecraft:creaking,tag=le.gcnew] le.gdt = #gt le.gd
scoreboard players add @e[type=minecraft:creaking,tag=le.gcnew] le.gdt 1200
tag @e[type=minecraft:creaking,tag=le.gcnew] remove le.gcnew
particle minecraft:block_crumble{block_state:"minecraft:pale_oak_wood"} ~ ~1 ~ 0.4 0.9 0.4 0 40 force @a[distance=..48]
playsound minecraft:entity.creaking.spawn hostile @a[distance=..32] ~ ~ ~ 1 0.8
playsound minecraft:block.creaking_heart.spawn block @a[distance=..32] ~ ~ ~ 0.8 0.7
scoreboard players add #wk le.gd 1
