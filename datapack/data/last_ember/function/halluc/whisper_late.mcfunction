# as a player at himself (from halluc/loop, when his le.hwl counts down to 0): a whispering voice 3-5 blocks behind him, for him only
scoreboard players reset @s le.hwl
execute store result score #k le.h run random value 1..4
execute if score #k le.h matches 1 positioned ^1 ^0.5 ^-4 run playsound last_ember:sfx.mind.whisper.1 ambient @s ~ ~ ~ 0.8 1
execute if score #k le.h matches 2 positioned ^-1 ^0.5 ^-3 run playsound last_ember:sfx.mind.whisper.2 ambient @s ~ ~ ~ 0.8 1
execute if score #k le.h matches 3 positioned ^ ^0.5 ^-5 run playsound last_ember:sfx.mind.whisper.3 ambient @s ~ ~ ~ 0.8 1
execute if score #k le.h matches 4 positioned ^2 ^0.5 ^-3 run playsound last_ember:sfx.mind.whisper.4 ambient @s ~ ~ ~ 0.8 1
