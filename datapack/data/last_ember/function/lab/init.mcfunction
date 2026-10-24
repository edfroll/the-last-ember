# as a freshly summoned sample (tag le.lnew); the state is le.ls: 0 dormant (the row), 1 appearing, 2 alive, 3 dying, 5 under the ground (the silverfish)
tag @s remove le.lnew
execute unless score @s le.ls matches 0.. run scoreboard players set @s le.ls 1
scoreboard players set @s le.lt 0
execute store result score @s le.lhp run data get entity @s Health
execute store result score @s le.lx run data get entity @s Pos[0] 100
execute store result score @s le.lz run data get entity @s Pos[2] 100
execute store result score @s le.lid run random value 40..100
scoreboard players set @s le.lcd 0
scoreboard players set @s le.lpc 0
scoreboard players set @s le.lfd 0
scoreboard players set @s le.lfr 0
scoreboard players set @s le.lan 0
scoreboard players set @s le.llook 6
scoreboard players set @s le.lair 0
scoreboard players set @s le.lsq 0
scoreboard players set @s le.lfl 0
