# advancement reward: a trap arrow hit this player. At most 3 hits (6 points) per firing: the arrows still in the air are removed; never below one heart.
advancement revoke @s only last_ember:trap/arrow_hit
scoreboard players add @s le.tbud 1
execute if score @s le.tbud matches 3.. run kill @e[type=minecraft:arrow,tag=le.trap_arrow,distance=..48]
execute store result score #hp le.tr run data get entity @s Health
execute if score #hp le.tr matches ..1 run effect give @s minecraft:instant_health 1 0 true
