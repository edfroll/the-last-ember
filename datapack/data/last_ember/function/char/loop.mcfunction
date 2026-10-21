# every tick (T-009): arrows, ashborn, second wind; every second: slow
execute store result score #gt le.e run time query gametime
function last_ember:char/arrows
execute as @a[tag=le.race.ashborn] run function last_ember:char/ash_tick
execute as @a[tag=le.race.human,gamemode=!spectator] run function last_ember:char/second_wind
scoreboard players add #cs le.e 1
execute if score #cs le.e matches 20.. run function last_ember:char/slow
schedule function last_ember:char/loop 1t replace
