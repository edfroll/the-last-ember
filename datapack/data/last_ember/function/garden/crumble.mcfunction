# T-025: as a creaking: it crumbles to dust (no drops, no death animation: the body goes 300 down and is killed)
particle minecraft:block_crumble{block_state:"minecraft:pale_oak_wood"} ~ ~1.3 ~ 0.35 0.9 0.35 0 60 force @a[distance=..48]
particle minecraft:block_crumble{block_state:"minecraft:pale_oak_log"} ~ ~0.6 ~ 0.3 0.4 0.3 0 25 force @a[distance=..48]
playsound minecraft:entity.creaking.death hostile @a[distance=..32] ~ ~ ~ 0.9 0.8
tag @s remove le.garden_cr
data merge entity @s {Invulnerable:1b,NoAI:1b,Silent:1b}
tp @s ~ ~-300 ~
kill @s
