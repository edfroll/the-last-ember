# every tick: the traps that are running; every 5 ticks the players are checked against the cell index; every second the hints, the build, the slow things
function last_ember:trap/gen/tick
scoreboard players add #t le.tr 1
scoreboard players operation #t5 le.tr = #t le.tr
scoreboard players operation #t5 le.tr %= #5 le.tr
execute if score #t5 le.tr matches 0 as @a[gamemode=!creative,gamemode=!spectator] at @s run function last_ember:trap/locate
execute if score #t5 le.tr matches 0 run function last_ember:trap/gen/chest_scan
execute if score #t5 le.tr matches 0 as @a run scoreboard players operation @s le.chopl = @s le.chop
scoreboard players operation #t20 le.tr = #t le.tr
scoreboard players operation #t20 le.tr %= #20 le.tr
execute if score #t20 le.tr matches 0 run function last_ember:trap/second
schedule function last_ember:trap/tick 1t replace
