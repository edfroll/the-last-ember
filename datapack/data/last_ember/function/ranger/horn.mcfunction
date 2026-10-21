# as a ranger: the horn was blown (the cooldown 30 s is the item's own use_cooldown). Hostile mobs within 24 (tier 0) .. 32 (tier 6) glow for 10 s.
advancement revoke @s only last_ember:ranger/horn
execute unless entity @s[tag=le.class.ranger] run return 0
scoreboard players operation #r le.e = @s le.tier
scoreboard players operation #r le.e *= #8 le.e
scoreboard players operation #r le.e /= #6 le.e
scoreboard players add #r le.e 24
execute store result storage last_ember:char tmp.r int 1 run scoreboard players get #r le.e
function last_ember:ranger/horn_m with storage last_ember:char tmp
playsound minecraft:item.goat_horn.sound.1 player @a[distance=..48] ~ ~ ~ 4 1
