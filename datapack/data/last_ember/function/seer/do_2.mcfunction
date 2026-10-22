# Blink: the ray from the eyes to the first solid block (or the range 12 .. 24 blocks), the landing = the last cell where the seer fits. 1 = done, 0 = no room (no cooldown spent)
execute if entity @s[tag=le.zf.no_blink] run return run function last_ember:seer/blink_fail
tag @s add le.caster
kill @e[type=marker,tag=le.ray]
summon marker ~ ~ ~ {Tags:["le.ray"]}
execute anchored eyes positioned ^ ^ ^ run tp @e[type=marker,tag=le.ray,limit=1,sort=nearest,distance=..3] ~ ~ ~ ~ ~
scoreboard players operation #n le.e = @s le.tier
scoreboard players operation #n le.e *= #4 le.e
scoreboard players add #n le.e 24
scoreboard players operation #st le.e = #n le.e
execute as @e[type=marker,tag=le.ray,limit=1] at @s run function last_ember:seer/blink_step
scoreboard players operation #st le.e -= #n le.e
execute if score #st le.e matches ..3 run return run function last_ember:seer/blink_fail
execute store result score #sc le.e run attribute @s minecraft:scale get 100
scoreboard players set #q le.e 162
scoreboard players operation #q le.e *= #sc le.e
scoreboard players operation #q le.e /= #100 le.e
scoreboard players remove #q le.e 2
execute store result storage last_ember:seer c.e double 0.01 run scoreboard players get #q le.e
scoreboard players set #k le.e 8
scoreboard players set #ok le.e 0
execute as @e[type=marker,tag=le.ray,limit=1] at @s store result score #ok le.e run function last_ember:seer/blink_land with storage last_ember:seer c
kill @e[type=marker,tag=le.ray]
tag @s remove le.caster
execute unless score #ok le.e matches 1 run return run function last_ember:seer/blink_fail
return 1
