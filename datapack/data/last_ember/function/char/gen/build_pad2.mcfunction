data modify storage last_ember:char built.pad2 set value 1b
summon minecraft:interaction 16.5 57 24.5 {width:3.0f,height:2.2f,response:1b,Tags:["le.cpad","le.cnew"]}
execute positioned 16.5 57 24.5 run scoreboard players set @e[type=minecraft:interaction,tag=le.cnew,distance=..1] le.pid 2
execute positioned 16.5 57 24.5 run tag @e[type=minecraft:interaction,tag=le.cnew,distance=..1] remove le.cnew
