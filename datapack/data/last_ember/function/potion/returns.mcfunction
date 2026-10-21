# as the cauldron: returned empty buckets / bottles for the used ingredients
execute store result score #t le.e run scoreboard players get @s le.cmask
scoreboard players operation #t le.e /= #1024 le.e
scoreboard players operation #t le.e %= #2 le.e
execute if score #t le.e matches 1 run summon minecraft:item ~ ~0.6 ~ {Item:{id:"minecraft:bucket",count:1},Motion:[0.0d,0.2d,0.2d]}
execute store result score #t le.e run scoreboard players get @s le.cmask
scoreboard players operation #t le.e /= #2048 le.e
scoreboard players operation #t le.e %= #2 le.e
execute if score #t le.e matches 1 run summon minecraft:item ~ ~0.6 ~ {Item:{id:"minecraft:glass_bottle",count:1},Motion:[0.0d,0.2d,0.2d]}
execute store result score #t le.e run scoreboard players get @s le.cmask
scoreboard players operation #t le.e /= #16384 le.e
scoreboard players operation #t le.e %= #2 le.e
execute if score #t le.e matches 1 run summon minecraft:item ~ ~0.6 ~ {Item:{id:"minecraft:bucket",count:1},Motion:[0.0d,0.2d,0.2d]}
