# the horizontal way made this tick (x100, |dx|+|dz|) -> le.lsp, summed in le.lst for the steps
execute store result score #x le.l run data get entity @s Pos[0] 100
execute store result score #z le.l run data get entity @s Pos[2] 100
scoreboard players operation #dx le.l = #x le.l
scoreboard players operation #dx le.l -= @s le.lx
scoreboard players operation #dz le.l = #z le.l
scoreboard players operation #dz le.l -= @s le.lz
execute if score #dx le.l matches ..-1 run scoreboard players operation #dx le.l *= #-1 le.l
execute if score #dz le.l matches ..-1 run scoreboard players operation #dz le.l *= #-1 le.l
scoreboard players operation #dx le.l += #dz le.l
execute if score #dx le.l matches 150.. run scoreboard players set #dx le.l 0
scoreboard players operation @s le.lsp = #dx le.l
scoreboard players operation @s le.lst += #dx le.l
scoreboard players operation @s le.lx = #x le.l
scoreboard players operation @s le.lz = #z le.l
