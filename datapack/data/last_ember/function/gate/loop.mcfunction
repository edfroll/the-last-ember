# every tick: players in transfer (only while someone is in one); every 5 ticks the triggers and the sky guard; every second the visuals
execute if entity @a[tag=le.sct,limit=1] as @a[tag=le.sct] at @s run function last_ember:gate/sc_tick
scoreboard players add #t le.gate 1
scoreboard players operation #t5 le.gate = #t le.gate
scoreboard players operation #t5 le.gate %= #5 le.gate
execute if score #t5 le.gate matches 0 run function last_ember:gate/five
execute as @e[type=minecraft:ender_pearl] at @s if entity @s[y=316,dy=2000] run function last_ember:gate/gen/pearl
schedule function last_ember:gate/loop 1t replace
