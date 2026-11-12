# every 5 ticks: the transfer triggers of open shortcuts, the sky guard over the border axes; every 4th time: the visuals (1 s)
execute store result score #gt le.gate run time query gametime
function last_ember:gate/gen/fast
execute as @a[tag=le.zf.border] at @s run function last_ember:gate/gen/sky
scoreboard players add #t20 le.gate 1
execute if score #t20 le.gate matches 4.. run scoreboard players set #t20 le.gate 0
execute if score #t20 le.gate matches 0 run function last_ember:gate/gen/sec
