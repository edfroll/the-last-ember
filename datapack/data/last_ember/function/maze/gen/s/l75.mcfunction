# generated: the player looks at statue 75 (within 20 degrees)
tag @s add le.mzlook
execute unless score @s le.mzs matches 75 run scoreboard players set @s le.mzg 0
scoreboard players set @s le.mzs 75
scoreboard players add @s le.mzg 5
execute if score @s le.mzg matches 20.. run function last_ember:maze/gen/s/f75
