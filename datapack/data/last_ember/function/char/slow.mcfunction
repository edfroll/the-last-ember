# every second
scoreboard players set #cs le.e 0
execute as @a[gamemode=!spectator,gamemode=!creative,tag=!le.cinit] run function last_ember:char/newcomer
execute as @a[scores={le.race=1..}] run function last_ember:char/refresh
function last_ember:char/gen/build_points
function last_ember:char/passes
function last_ember:char/grate_check
execute as @a[tag=le.class.knight,gamemode=!spectator] at @s run function last_ember:knight/second
execute as @a[tag=le.sated] run function last_ember:knight/sated_second
execute as @a[tag=le.class.healer,gamemode=!spectator] run function last_ember:potion/scan
