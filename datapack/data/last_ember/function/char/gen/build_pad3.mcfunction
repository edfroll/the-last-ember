data modify storage last_ember:char built.pad3 set value 1b
summon minecraft:interaction -15.5 57 24.5 {width:3.0f,height:2.2f,response:1b,Tags:["le.cpad","le.cnew"]}
execute positioned -15.5 57 24.5 run scoreboard players set @e[type=minecraft:interaction,tag=le.cnew,distance=..1] le.pid 3
execute positioned -15.5 57 24.5 run tag @e[type=minecraft:interaction,tag=le.cnew,distance=..1] remove le.cnew
