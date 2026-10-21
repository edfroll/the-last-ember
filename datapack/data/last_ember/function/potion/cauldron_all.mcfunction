# every 4 ticks: all cauldrons over burning bonfires (interactions with the tag le.pot), and the healers' Amulets
scoreboard players set #c4 le.e 0
execute as @e[type=minecraft:interaction,tag=le.pot] at @s run function last_ember:potion/cauldron
execute as @a[tag=le.class.healer,gamemode=!spectator] at @s run function last_ember:potion/amulet
