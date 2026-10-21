tag @s add le.ar
scoreboard players set #rg le.e 0
scoreboard players set #el le.e 0
execute on origin if entity @s[type=minecraft:player,tag=le.class.ranger] run scoreboard players set #rg le.e 1
execute on origin if entity @s[type=minecraft:player,tag=le.race.elf] run scoreboard players set #el le.e 1
execute if score #rg le.e matches 1 run function last_ember:char/arrow_fast
execute if score #el le.e matches 1 run function last_ember:char/arrow_strong
