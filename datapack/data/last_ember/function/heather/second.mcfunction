# T-031: every second (in the overworld, players near the village): the difficulty, the day time, the hats against the sun, the old
# generations, the points of the dead villagers (alive / killed / back at dawn), the awake ones back home when nobody is within 32, the
# resting ones turn their heads now and then, the midnight bell, the ringer, the sails (every 2 s), the scarecrows
scoreboard players set #t le.hv 0
scoreboard players add #sec le.hv 1
scoreboard players enable @a le.htrig
function last_ember:heather/gen/near
execute if score #near le.hv matches 0 run return 0
execute store result score #df le.hv run difficulty
scoreboard players operation #pdt le.hv = #dt le.hv
execute store result score #ck le.hv run time query time
scoreboard players operation #day le.hv = #ck le.hv
scoreboard players operation #day le.hv /= #24000 le.hv
scoreboard players operation #dt le.hv = #ck le.hv
scoreboard players operation #dt le.hv %= #24000 le.hv
execute if score #df le.hv matches 0 run function last_ember:heather/gen/forget
function last_ember:heather/gen/hats
execute as @e[type=minecraft:zombie_villager,tag=le.hz] run function last_ember:heather/gen/genchk
function last_ember:heather/gen/points
execute as @e[type=minecraft:zombie_villager,tag=le.hza,tag=!le.hfrz] at @s unless entity @a[gamemode=!spectator,distance=..32] run function last_ember:heather/rest
execute as @e[type=minecraft:zombie_villager,tag=le.hzr,tag=!le.hfrz] if predicate last_ember:heather/look at @s run function last_ember:heather/look
execute as @e[type=minecraft:zombie_villager,tag=le.hzr,tag=!le.hfrz] if predicate last_ember:heather/sound at @s run playsound minecraft:entity.zombie_villager.ambient hostile @a ~ ~ ~ 0.8 0.85
execute if score #pdt le.hv matches ..17999 if score #dt le.hv matches 18000..18100 if score #nb le.hv matches 1.. run function last_ember:heather/bell
execute if score #frz le.hv matches 1.. run function last_ember:heather/frozen
execute as @e[type=minecraft:villager,tag=le.ringer] unless score @s le.hrg = #rgen le.hv run kill @s
execute as @e[type=minecraft:interaction,tag=le.htalk] unless score @s le.hrg = #rgen le.hv run kill @s
function last_ember:heather/gen/ringer_check
scoreboard players operation #s2 le.hv = #sec le.hv
scoreboard players operation #s2 le.hv %= #2 le.hv
execute if score #s2 le.hv matches 0 run function last_ember:heather/gen/mill
function last_ember:heather/gen/sails_check
function last_ember:heather/gen/scare_check
