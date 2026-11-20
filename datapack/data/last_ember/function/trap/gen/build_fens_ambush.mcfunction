# generated: build fens_ambush
scoreboard players set #fens_ambush_bl le.tr 1
execute in minecraft:overworld unless entity @e[type=minecraft:marker,tag=le.cc,scores={le.tid=1}] run summon minecraft:marker -478.5 135.5 367.5 {Tags:["le.cc"]}
execute in minecraft:overworld positioned -478 135 367 as @e[type=minecraft:marker,tag=le.cc,distance=..2,limit=1] unless score @s le.tid matches 1.. run scoreboard players set @s le.tid 1
