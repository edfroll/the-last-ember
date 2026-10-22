# as an enemy in reach, the caster is le.caster: the bearing to the caster and the strength N (front 6..9 / around 2..3)
execute as @e[type=marker,tag=le.sp_m,limit=1] run tp @s ~ ~ ~
tp @e[type=marker,tag=le.sp_m,limit=1] ~ ~ ~ facing entity @a[tag=le.caster,limit=1] feet
execute store result score #ay le.e run data get entity @e[type=marker,tag=le.sp_m,limit=1] Rotation[0]
scoreboard players operation #ay le.e -= #cy le.e
scoreboard players add #ay le.e 540
scoreboard players operation #ay le.e %= #360 le.e
scoreboard players set #front le.e 0
execute if score #ay le.e matches ..45 run scoreboard players set #front le.e 1
execute if score #ay le.e matches 315.. run scoreboard players set #front le.e 1
execute store result score #n le.e run data get storage last_ember:seer c.a
execute if score #front le.e matches 1 store result score #n le.e run data get storage last_ember:seer c.f
execute if score #front le.e matches 0 if entity @s[tag=le.sp_far] run return 0
execute if score #front le.e matches 0 run scoreboard players set #front le.e 0
execute store result score #mx le.e run data get entity @s Pos[0] 1000
execute store result score #mz le.e run data get entity @s Pos[2] 1000
execute as @e[type=marker,tag=le.sp_m,limit=1] at @s rotated ~ 0 run tp @s ^ ^ ^-1
execute store result score #dx le.e run data get entity @e[type=marker,tag=le.sp_m,limit=1] Pos[0] 1000
execute store result score #dz le.e run data get entity @e[type=marker,tag=le.sp_m,limit=1] Pos[2] 1000
scoreboard players operation #dx le.e -= #mx le.e
scoreboard players operation #dz le.e -= #mz le.e
scoreboard players operation #n le.e *= #kb le.e
scoreboard players operation #dx le.e *= #n le.e
scoreboard players operation #dz le.e *= #n le.e
scoreboard players operation #dx le.e /= #1000 le.e
scoreboard players operation #dz le.e /= #1000 le.e
execute store result entity @s Motion[0] double 0.001 run scoreboard players get #dx le.e
execute store result entity @s Motion[2] double 0.001 run scoreboard players get #dz le.e
data modify entity @s Motion[1] set value 0.35d
execute at @s run particle minecraft:poof ~ ~0.5 ~ 0.2 0.3 0.2 0.05 6
