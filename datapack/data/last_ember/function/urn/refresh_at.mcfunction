execute as @e[type=minecraft:text_display,tag=le.urn_plate,distance=..8] if score @s le.uid = #u le.e run data modify entity @s text set from storage last_ember:dt pt
execute if score #lit le.e matches 1 run fill ~-1 ~6 ~-1 ~1 ~6 ~1 minecraft:candle[lit=true] replace minecraft:air
execute if score #lit le.e matches 1 run fill ~-1 ~6 ~-1 ~1 ~6 ~1 minecraft:candle[lit=true] replace minecraft:candle
execute if score #lit le.e matches 0 run fill ~-1 ~6 ~-1 ~1 ~6 ~1 minecraft:candle[lit=false] replace minecraft:air
execute if score #lit le.e matches 0 run fill ~-1 ~6 ~-1 ~1 ~6 ~1 minecraft:candle[lit=false] replace minecraft:candle
setblock ~ ~6 ~ minecraft:gray_carpet
setblock ~ ~6 ~-1 minecraft:air
setblock ~ ~6 ~1 minecraft:air
setblock ~-1 ~6 ~ minecraft:air
setblock ~1 ~6 ~ minecraft:air
execute if score #lit le.e matches 1 as @e[type=minecraft:text_display,tag=le.urn_plate,distance=..8] if score @s le.uid = #u le.e run tag @s add le.urn_lit
execute if score #lit le.e matches 0 as @e[type=minecraft:text_display,tag=le.urn_plate,distance=..8] if score @s le.uid = #u le.e run tag @s remove le.urn_lit
