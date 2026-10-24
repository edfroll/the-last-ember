# every second: the insomnia of every player (survival and adventure)
execute as @a[gamemode=!spectator,gamemode=!creative] at @s run function last_ember:halluc/second
# the late whispers (halluc/whisper): seconds left in le.hwl
scoreboard players remove @a[scores={le.hwl=1..}] le.hwl 1
execute as @a[scores={le.hwl=0}] at @s run function last_ember:halluc/whisper_late
# markers whose player went away do not stay: 6 s of life
execute as @e[type=minecraft:marker,tag=le.hmark] run scoreboard players remove @s le.hst 1
kill @e[type=minecraft:marker,tag=le.hmark,scores={le.hst=..-1}]
schedule function last_ember:halluc/loop 20t replace
