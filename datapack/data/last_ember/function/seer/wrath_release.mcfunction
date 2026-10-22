# the button is released (or the charge is full): the bolt into the point of the gaze (a ray up to 48 blocks to the first solid block); damage from 6+t to 30+5t by the charge
tag @s add le.caster
scoreboard players operation #c le.e = @s le.wchg
scoreboard players set @s le.wchg -1
scoreboard players operation @s le.cd7 = #gt le.e
scoreboard players add @s le.cd7 300
scoreboard players operation #nc le.e = @s le.tier
scoreboard players add #nc le.e 6
scoreboard players operation #fu le.e = @s le.tier
scoreboard players operation #fu le.e *= #5 le.e
scoreboard players add #fu le.e 30
scoreboard players operation #fu le.e -= #nc le.e
scoreboard players operation #fu le.e *= #c le.e
scoreboard players operation #fu le.e /= #200 le.e
scoreboard players operation #fu le.e += #nc le.e
execute store result storage last_ember:seer c.dm int 1 run scoreboard players get #fu le.e
scoreboard players operation #fu le.e /= #2 le.e
execute if score #fu le.e matches ..0 run scoreboard players set #fu le.e 1
execute store result storage last_ember:seer c.hm int 1 run scoreboard players get #fu le.e
kill @e[type=marker,tag=le.ray]
summon marker ~ ~ ~ {Tags:["le.ray"]}
execute anchored eyes positioned ^ ^ ^ run tp @e[type=marker,tag=le.ray,limit=1,sort=nearest,distance=..3] ~ ~ ~ ~ ~
scoreboard players set #n le.e 96
execute as @e[type=marker,tag=le.ray,limit=1] at @s run function last_ember:seer/blink_step
execute as @e[type=marker,tag=le.ray,limit=1] at @s run function last_ember:seer/wrath_strike with storage last_ember:seer c
kill @e[type=marker,tag=le.ray]
tag @s remove le.caster
function last_ember:seer/hint
