# at the centre of the cell of the feet: two free blocks (the body is 2 blocks high at any scale), no lava, ground within 40 blocks below; then the move
execute unless block ~ ~ ~ #last_ember:blink_pass run return 0
execute unless block ~ ~1 ~ #last_ember:blink_pass run return 0
scoreboard players set #gr le.e 0
scoreboard players set #g le.e 40
execute positioned ~ ~-1 ~ run function last_ember:seer/blink_ground
execute unless score #gr le.e matches 1 run return 0
execute as @a[tag=le.caster,limit=1] at @s run particle minecraft:reverse_portal ~ ~1 ~ 0.3 0.6 0.3 0.1 40
execute as @a[tag=le.caster,limit=1] at @s run playsound minecraft:entity.enderman.teleport player @a[distance=..20] ~ ~ ~ 0.6 1.5
tp @a[tag=le.caster,limit=1] ~ ~ ~
execute as @a[tag=le.caster,limit=1] at @s run particle minecraft:portal ~ ~1 ~ 0.3 0.6 0.3 0.4 40
execute as @a[tag=le.caster,limit=1] at @s run playsound minecraft:entity.enderman.teleport player @a[distance=..20] ~ ~ ~ 0.6 1.9
return 1
