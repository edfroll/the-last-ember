# T-032: at a player's feet (air, in the nest): cobweb for 5 s (a marker takes it away)
setblock ~ ~ ~ minecraft:cobweb
summon minecraft:marker ~ ~ ~ {Tags:["le.spweb","le.spwnew"]}
scoreboard players operation @e[type=minecraft:marker,tag=le.spwnew] le.spwt = #gt le.sp
scoreboard players add @e[type=minecraft:marker,tag=le.spwnew] le.spwt 100
tag @e[type=minecraft:marker,tag=le.spwnew] remove le.spwnew
particle minecraft:block{block_state:"minecraft:cobweb"} ~ ~0.6 ~ 0.4 0.4 0.4 0 25
scoreboard players add #webs le.sp 1
