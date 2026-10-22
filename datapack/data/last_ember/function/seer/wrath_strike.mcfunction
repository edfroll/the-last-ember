# macro dm / hm: at the point of the strike: damage to the enemies within 2 blocks (half to bosses and giants), fire 3x3 in the safe places, light and thunder instead of a vanilla bolt
$execute as @e[type=#last_ember:monsters,tag=!le.npc,tag=!le.boss,tag=!le.giant,distance=..2] run damage @s $(dm) minecraft:lightning_bolt by @a[tag=le.caster,limit=1]
$execute as @e[type=#last_ember:monsters,tag=!le.npc,distance=..2,tag=le.boss] run damage @s $(hm) minecraft:lightning_bolt by @a[tag=le.caster,limit=1]
$execute as @e[type=#last_ember:monsters,tag=!le.npc,distance=..2,tag=le.giant,tag=!le.boss] run damage @s $(hm) minecraft:lightning_bolt by @a[tag=le.caster,limit=1]
particle minecraft:electric_spark ~ ~8 ~ 0.12 8 0.12 0.3 150 force
particle minecraft:electric_spark ~ ~0.3 ~ 1 0.2 1 0.4 50 force
particle minecraft:explosion ~ ~0.3 ~ 0.6 0.1 0.6 0 3 force
particle minecraft:large_smoke ~ ~0.3 ~ 0.5 0.2 0.5 0.05 15 force
playsound minecraft:entity.lightning_bolt.thunder weather @a[distance=..64] ~ ~ ~ 4 1.0
playsound minecraft:entity.lightning_bolt.impact weather @a[distance=..64] ~ ~ ~ 3 1.0
execute positioned ~-1 ~ ~-1 run function last_ember:seer/fire_one
execute positioned ~-1 ~ ~ run function last_ember:seer/fire_one
execute positioned ~-1 ~ ~1 run function last_ember:seer/fire_one
execute positioned ~ ~ ~-1 run function last_ember:seer/fire_one
execute positioned ~ ~ ~ run function last_ember:seer/fire_one
execute positioned ~ ~ ~1 run function last_ember:seer/fire_one
execute positioned ~1 ~ ~-1 run function last_ember:seer/fire_one
execute positioned ~1 ~ ~ run function last_ember:seer/fire_one
execute positioned ~1 ~ ~1 run function last_ember:seer/fire_one
function last_ember:seer/fire_loop
