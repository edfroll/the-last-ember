# T-031: a button of the ringer's windows (trigger le.htrig: 1 who are you, 2 the village, 3 «Найдём», 4 the menu, 5 the grandson;
# T-032: q >= 2 - «Тойво дома», le.hwin 9; the reward window spiders/ringer_talk is le.hwin 8):
# only within 6 of the ringer; the window goes to the one who pressed
scoreboard players operation #k le.hv = @s le.htrig
scoreboard players set @s le.htrig 0
scoreboard players enable @s le.htrig
execute unless entity @e[type=minecraft:villager,tag=le.ringer,distance=..6] run return 0
execute store result score #q le.hv run data get storage last_ember:heather q
execute if score #k le.hv matches 1 run scoreboard players set @s le.hwin 2
execute if score #k le.hv matches 1 run return run dialog show @s last_ember:heather/about
execute if score #k le.hv matches 2 run scoreboard players set @s le.hwin 3
execute if score #k le.hv matches 2 run return run dialog show @s last_ember:heather/village
execute if score #k le.hv matches 3 if score #q le.hv matches 0 run data modify storage last_ember:heather q set value 1
execute if score #k le.hv matches 3 run return run scoreboard players set @s le.hwin 7
execute if score #k le.hv matches 4 run return run function last_ember:heather/menu
execute if score #k le.hv matches 5 if score #q le.hv matches 2.. run scoreboard players set @s le.hwin 9
execute if score #k le.hv matches 5 if score #q le.hv matches 2.. run return run dialog show @s last_ember:spiders/ringer_grandson
execute if score #k le.hv matches 5 if score #q le.hv matches 1.. run scoreboard players set @s le.hwin 5
execute if score #k le.hv matches 5 if score #q le.hv matches 1.. run return run dialog show @s last_ember:heather/grandson
execute if score #k le.hv matches 5 run scoreboard players set @s le.hwin 6
execute if score #k le.hv matches 5 run return run dialog show @s last_ember:heather/about
