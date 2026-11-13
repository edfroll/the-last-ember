# generated: the shortcut door of r1 is placed (template, locked) once its chunk is loaded
place template last_ember:shortcut/door_r1 -388 110 -192 counterclockwise_90
kill @e[type=minecraft:interaction,tag=le.scdoor,scores={le.scw=1}]
summon minecraft:interaction -378.5 111 -195.5 {Tags:["le.scdoor","le.scclick","le.scnew"],width:1.2f,height:2.2f,response:1b}
scoreboard players set @e[type=minecraft:interaction,tag=le.scnew] le.scw 1
tag @e[type=minecraft:interaction,tag=le.scnew] remove le.scnew
scoreboard players set #scb_r1 le.gate 1
scoreboard players set #scvd_r1 le.gate 0
