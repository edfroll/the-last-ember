# as a knight, every second: standing 60 s at a lit bonfire (radius 6) not in battle (no damage taken for 10 s) -> the Blessing, once per game day
execute store result score #dt le.e run scoreboard players get @s le.dtk
execute unless score @s le.dlast = #dt le.e run function last_ember:knight/hurt
execute if score @s le.hurtcd matches 1.. run scoreboard players remove @s le.hurtcd 1
scoreboard players set #lit le.e 0
execute as @e[type=minecraft:interaction,tag=le.hearth,distance=..6] run function last_ember:knight/hearth_lit
# game day = 24000 ticks of the game time (26.3: `time query day` is the time of day, not a counter)
scoreboard players operation #day le.e = #gt le.e
scoreboard players operation #day le.e /= #24000 le.e
execute if score #lit le.e matches 0 run return run scoreboard players set @s le.bless 0
execute if score @s le.hurtcd matches 1.. run return run scoreboard players set @s le.bless 0
execute if score @s le.blday = #day le.e run return run function last_ember:knight/tomorrow
scoreboard players add @s le.bless 1
execute if score @s le.bless matches 30 run title @s actionbar {"text":"Благословение — ещё 30 секунд","color":"gold"}
execute if score @s le.bless matches 60.. run function last_ember:knight/bless
