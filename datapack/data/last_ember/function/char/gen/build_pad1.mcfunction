data modify storage last_ember:char built.pad1 set value 1b
summon minecraft:interaction 12.5 57 12.5 {width:3.0f,height:2.2f,response:1b,Tags:["le.cpad","le.cnew"]}
execute positioned 12.5 57 12.5 run scoreboard players set @e[type=minecraft:interaction,tag=le.cnew,distance=..1] le.pid 1
execute positioned 12.5 57 12.5 run tag @e[type=minecraft:interaction,tag=le.cnew,distance=..1] remove le.cnew
