data modify storage last_ember:char built.altar2 set value 1b
summon minecraft:interaction 5.5 54.5 52.5 {width:5.0f,height:4.0f,response:1b,Tags:["le.cpad","le.cnew"]}
execute positioned 5.5 54.5 52.5 run scoreboard players set @e[type=minecraft:interaction,tag=le.cnew,distance=..1] le.pid 12
execute positioned 5.5 54.5 52.5 run tag @e[type=minecraft:interaction,tag=le.cnew,distance=..1] remove le.cnew
summon minecraft:item_display 5.5 59.1 52.5 {Tags:["le.csym"],billboard:"vertical",item:{id:"minecraft:goat_horn",count:1},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.9f,0.9f,0.9f]}}
