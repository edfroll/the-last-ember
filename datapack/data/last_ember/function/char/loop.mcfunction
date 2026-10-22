# every tick (T-009): arrows, ashborn, second wind; every second: slow
execute store result score #gt le.e run time query gametime
function last_ember:char/arrows
execute as @a[tag=le.race.ashborn] run function last_ember:char/ash_tick
execute as @a[tag=le.race.human,gamemode=!spectator] run function last_ember:char/second_wind
execute as @a[tag=le.immune] run function last_ember:potion/immune_tick
execute as @a[scores={le.suse=1..}] at @s run function last_ember:seer/released_check
execute if score #wact le.e matches 1 unless entity @a[scores={le.wchg=0..}] run function last_ember:seer/weather_restore
execute as @a[tag=le.class.seer,gamemode=!spectator] run function last_ember:seer/xp_tick
execute as @a[tag=le.grchk] run function last_ember:seer/grimoire_fix
scoreboard players add #c4 le.e 1
execute if score #c4 le.e matches 4.. run function last_ember:potion/cauldron_all
scoreboard players add #cs le.e 1
execute if score #cs le.e matches 20.. run function last_ember:char/slow
schedule function last_ember:char/loop 1t replace
