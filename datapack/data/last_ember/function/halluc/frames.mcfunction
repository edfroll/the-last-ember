# every 4 ticks: the shadows that are on the screen of a player
execute as @a[scores={le.hst=1..}] at @s run function last_ember:halluc/shadow_frame
schedule function last_ember:halluc/frames 4t replace
