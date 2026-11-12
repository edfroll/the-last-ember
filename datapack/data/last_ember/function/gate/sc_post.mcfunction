# as a player just after the teleport: the pets follow, the darkness falls off in ~1 s, 3 s cooldown (no ping-pong)
tp @e[tag=le.scpet] @s
tag @e[tag=le.scpet] remove le.scpet
tag @s remove le.scme
function last_ember:gate/sc_cancel
execute if entity @s[gamemode=!spectator,gamemode=!creative] run effect give @s minecraft:blindness 1 0 true
scoreboard players operation @s le.sccd = #gt le.gate
scoreboard players add @s le.sccd 65
execute at @s run playsound minecraft:block.wooden_door.close player @s ~ ~ ~ 0.5 0.7
