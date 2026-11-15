# generated: the player looks at statue 88 (within 20 degrees)
tag @s add le.mzlook
execute unless score @s le.mzs matches 88 run scoreboard players set @s le.mzg 0
scoreboard players set @s le.mzs 88
scoreboard players add @s le.mzg 5
execute if score @s le.mzg matches 20.. run function last_ember:maze/gen/s/f88
