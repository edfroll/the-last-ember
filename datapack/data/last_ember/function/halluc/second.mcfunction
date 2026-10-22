# as a player at himself, once a second: the stage of the insomnia from the vanilla "time since rest" (it is reset by every bed, also the straw one)
scoreboard players set #st le.h 0
execute if score @s le.rest matches 24000.. run scoreboard players set #st le.h 1
execute if score @s le.rest matches 36000.. run scoreboard players set #st le.h 2
execute if score @s le.rest matches 48000.. run scoreboard players set #st le.h 3
execute if score @s le.rest matches 72000.. run scoreboard players set #st le.h 4
execute unless score @s le.hstg matches 0..4 run scoreboard players set @s le.hstg 0
execute if score @s le.hstg matches 2.. if score #st le.h matches 0 run title @s actionbar {"text":"Ты наконец выспался","color":"gray"}
execute if score #st le.h matches 0 run function last_ember:halluc/clear
execute if score #st le.h > @s le.hstg run function last_ember:halluc/stage_msg
scoreboard players operation @s le.hstg = #st le.h
execute if score #st le.h matches 0 run return 0
execute if entity @s[tag=le.zf.calm] run return 0
function last_ember:halluc/timers
execute if score #st le.h matches 3.. run effect give @s minecraft:slowness 2 0 true
execute if score #st le.h matches 4.. run effect give @s minecraft:weakness 2 0 true
