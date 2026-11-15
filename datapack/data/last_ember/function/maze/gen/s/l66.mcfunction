# generated: the player looks at statue 66 (within 20 degrees)
tag @s add le.mzlook
execute unless score @s le.mzs matches 66 run scoreboard players set @s le.mzg 0
scoreboard players set @s le.mzs 66
scoreboard players add @s le.mzg 5
execute if score @s le.mzg matches 20.. run function last_ember:maze/gen/s/f66
