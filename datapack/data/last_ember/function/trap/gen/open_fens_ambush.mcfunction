# the first opening of the cursed chest: mobs 2 + 1 per player within 16
execute unless score #fens_ambush_st le.tr matches 0 run return 0
scoreboard players set #fens_ambush_st le.tr 2
execute in minecraft:overworld positioned -478 135 367 store result score #cnt le.tr if entity @a[distance=..16]
scoreboard players add #cnt le.tr 2
execute in minecraft:overworld positioned -478 135 367 run function last_ember:trap/spawn_ring {mob:"minecraft:drowned",mob2:"minecraft:bogged"}
execute in minecraft:overworld positioned -478 135 367 run playsound minecraft:entity.wither.ambient block @a[distance=..20] ~ ~ ~ 0.8 0.6
execute in minecraft:overworld positioned -478 135 367 run particle minecraft:soul ~ ~1 ~ 1 0.5 1 0.05 30 force
