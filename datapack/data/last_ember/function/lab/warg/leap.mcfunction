# out of the bushes: visible, a snarl, a leap toward the nearest player (Motion from a marker 0.75 blocks along the look)
effect clear @s minecraft:invisibility
# the glowing eyes are for the ambush only: on a vanilla wolf model they cannot follow the turns of the head
execute on passengers run kill @s
playsound last_ember:creature.wild_dog.snarl hostile @a ~ ~ ~ 1.8 1
particle minecraft:block{block_state:"minecraft:oak_leaves"} ~ ~0.8 ~ 0.8 0.4 0.8 0.1 40
function last_ember:lab/awake
execute facing entity @p[distance=..24] feet positioned 0.0 0.0 0.0 positioned ^ ^ ^0.75 run summon minecraft:marker ~ ~ ~ {Tags:["le.lvec"]}
data modify entity @s Motion set from entity @e[type=minecraft:marker,tag=le.lvec,limit=1] Pos
data modify entity @s Motion[1] set value 0.55d
kill @e[type=minecraft:marker,tag=le.lvec]
