data modify storage last_ember:char built.altar1 set value 1b
summon minecraft:interaction -4.5 54.5 52.5 {width:5.0f,height:4.0f,response:1b,Tags:["le.cpad","le.cnew"]}
execute positioned -4.5 54.5 52.5 run scoreboard players set @e[type=minecraft:interaction,tag=le.cnew,distance=..1] le.pid 11
execute positioned -4.5 54.5 52.5 run tag @e[type=minecraft:interaction,tag=le.cnew,distance=..1] remove le.cnew
summon minecraft:item_display -4.5 59.1 52.5 {Tags:["le.csym"],billboard:"vertical",item:{id:"minecraft:shield",count:1},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.9f,0.9f,0.9f]}}
