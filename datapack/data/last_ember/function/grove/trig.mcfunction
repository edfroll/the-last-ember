# T-030: a button of the Advisor's windows (trigger le.atrig: 1 menu, 2 castle, 3 maze, 4 pale garden, 5 fens, 6 Weepers, 7 about him):
# only within 6 of the Advisor; the window goes to the one who pressed
scoreboard players operation #k le.grv = @s le.atrig
scoreboard players set @s le.atrig 0
scoreboard players enable @s le.atrig
execute unless entity @e[type=minecraft:mannequin,tag=le.advisor,distance=..6] run return 0
execute if score #k le.grv matches 1 run return run function last_ember:grove/menu
execute if score #k le.grv matches 2..7 run scoreboard players operation @s le.awin = #k le.grv
execute if score #k le.grv matches 2..7 run scoreboard players add @s le.awin 10
execute if score #k le.grv matches 2 run return run dialog show @s last_ember:grove/castle
execute if score #k le.grv matches 3 run return run dialog show @s last_ember:grove/maze
execute if score #k le.grv matches 4 run return run dialog show @s last_ember:grove/garden
execute if score #k le.grv matches 5 run return run dialog show @s last_ember:grove/fens
execute if score #k le.grv matches 6 run return run dialog show @s last_ember:grove/weepers
execute if score #k le.grv matches 7 run return run dialog show @s last_ember:grove/self
