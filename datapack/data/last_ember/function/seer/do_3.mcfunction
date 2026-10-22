# Frost: the enemies around (radius 6 .. 12): Slowness + Weakness (I, II from the tier 3 is level 2; tier 0-2: I) for 10 s and the frost view (TicksFrozen kept under the damage threshold); no damage
scoreboard players operation #r le.e = @s le.tier
scoreboard players add #r le.e 6
execute store result storage last_ember:seer c.r int 1 run scoreboard players get #r le.e
scoreboard players operation #a le.e = @s le.tier
scoreboard players operation #a le.e /= #3 le.e
execute if score #a le.e matches 2.. run scoreboard players set #a le.e 1
execute store result storage last_ember:seer c.a int 1 run scoreboard players get #a le.e
function last_ember:seer/do_3_m with storage last_ember:seer c
particle minecraft:snowflake ~ ~1 ~ 1 0.6 1 0.05 60
playsound minecraft:block.glass.break player @a[distance=..20] ~ ~ ~ 0.8 0.5
playsound minecraft:entity.player.hurt_freeze player @a[distance=..20] ~ ~ ~ 0.8 0.8
return 1
