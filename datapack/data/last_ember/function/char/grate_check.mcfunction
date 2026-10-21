# when every player on the server has chosen (class), four fires light at the grate on the square (once)
execute if score #grate le.e matches 1 run return 0
execute unless entity @a[scores={le.class=1..}] run return 0
execute if entity @a[gamemode=!spectator,gamemode=!creative,scores={le.class=..0}] run return 0
execute if entity @a[gamemode=!spectator,gamemode=!creative,tag=!le.cinit] run return 0
scoreboard players set #grate le.e 1
setblock -2 103 22 minecraft:campfire[lit=true,signal_fire=false]
setblock 2 103 22 minecraft:campfire[lit=true,signal_fire=false]
setblock -2 103 26 minecraft:campfire[lit=true,signal_fire=false]
setblock 2 103 26 minecraft:campfire[lit=true,signal_fire=false]
