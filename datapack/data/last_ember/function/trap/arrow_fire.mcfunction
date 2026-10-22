# at a point of the wall, facing the target: one arrow (2 points of damage: 1.6 x 1.2 = 1.92) with a little scatter
summon minecraft:arrow ^ ^ ^0.6 {Tags:["le.trap_arrow","le.anew"],damage:1.2d,pickup:0b,Motion:[0.0d,0.0d,0.0d]}
summon minecraft:marker ^ ^ ^1.6 {Tags:["le.amk"]}
execute as @e[type=minecraft:arrow,tag=le.anew,limit=1] store result score #ax le.tr run data get entity @s Pos[0] 1000
execute as @e[type=minecraft:arrow,tag=le.anew,limit=1] store result score #ay le.tr run data get entity @s Pos[1] 1000
execute as @e[type=minecraft:arrow,tag=le.anew,limit=1] store result score #az le.tr run data get entity @s Pos[2] 1000
execute as @e[type=minecraft:marker,tag=le.amk,limit=1] store result score #mx le.tr run data get entity @s Pos[0] 1000
execute as @e[type=minecraft:marker,tag=le.amk,limit=1] store result score #my le.tr run data get entity @s Pos[1] 1000
execute as @e[type=minecraft:marker,tag=le.amk,limit=1] store result score #mz le.tr run data get entity @s Pos[2] 1000
scoreboard players operation #vx le.tr = #mx le.tr
scoreboard players operation #vx le.tr -= #ax le.tr
scoreboard players operation #vy le.tr = #my le.tr
scoreboard players operation #vy le.tr -= #ay le.tr
scoreboard players operation #vz le.tr = #mz le.tr
scoreboard players operation #vz le.tr -= #az le.tr
scoreboard players operation #vx le.tr *= #16 le.tr
scoreboard players operation #vy le.tr *= #16 le.tr
scoreboard players operation #vz le.tr *= #16 le.tr
scoreboard players operation #vx le.tr /= #10 le.tr
scoreboard players operation #vy le.tr /= #10 le.tr
scoreboard players operation #vz le.tr /= #10 le.tr
execute store result score #r le.tr run random value -50..50
scoreboard players operation #vx le.tr += #r le.tr
execute store result score #r le.tr run random value -50..50
scoreboard players operation #vz le.tr += #r le.tr
execute store result score #r le.tr run random value -25..25
scoreboard players operation #vy le.tr += #r le.tr
execute as @e[type=minecraft:arrow,tag=le.anew,limit=1] store result entity @s Motion[0] double 0.001 run scoreboard players get #vx le.tr
execute as @e[type=minecraft:arrow,tag=le.anew,limit=1] store result entity @s Motion[1] double 0.001 run scoreboard players get #vy le.tr
execute as @e[type=minecraft:arrow,tag=le.anew,limit=1] store result entity @s Motion[2] double 0.001 run scoreboard players get #vz le.tr
tag @e[type=minecraft:arrow,tag=le.anew] remove le.anew
kill @e[type=minecraft:marker,tag=le.amk]
