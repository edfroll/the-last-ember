# generated: the player looks at statue 96 (within 20 degrees)
tag @s add le.mzlook
execute unless score @s le.mzs matches 96 run scoreboard players set @s le.mzg 0
scoreboard players set @s le.mzs 96
scoreboard players add @s le.mzg 5
execute if score @s le.mzg matches 20.. run function last_ember:maze/gen/s/f96
