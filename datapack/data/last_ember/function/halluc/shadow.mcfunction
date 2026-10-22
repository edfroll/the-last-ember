# MODULE: as a player at himself: a silhouette of dark particles at the edge of his view, 10-16 blocks to the side; it goes after 1-2 s or when he turns to it. No entity is shown to anyone (a server-side marker only holds the place); the particles are forced to him only.
execute if score @s le.hst matches 1.. run return 0
function last_ember:halluc/ensure_id
scoreboard players operation #me le.h = @s le.hid
execute store result score #k le.h run random value 0..5
execute if score #k le.h matches 0 positioned ^-10 ^ ^3 run summon minecraft:marker ~ ~ ~ {Tags:["le.hmark"]}
execute if score #k le.h matches 1 positioned ^10 ^ ^3 run summon minecraft:marker ~ ~ ~ {Tags:["le.hmark"]}
execute if score #k le.h matches 2 positioned ^-13 ^ ^5 run summon minecraft:marker ~ ~ ~ {Tags:["le.hmark"]}
execute if score #k le.h matches 3 positioned ^13 ^ ^5 run summon minecraft:marker ~ ~ ~ {Tags:["le.hmark"]}
execute if score #k le.h matches 4 positioned ^-15 ^ ^1 run summon minecraft:marker ~ ~ ~ {Tags:["le.hmark"]}
execute if score #k le.h matches 5 positioned ^15 ^ ^1 run summon minecraft:marker ~ ~ ~ {Tags:["le.hmark"]}
execute as @e[type=minecraft:marker,tag=le.hmark,tag=!le.hset,distance=..30] run function last_ember:halluc/mark_set
execute store result score @s le.hst run random value 5..10
