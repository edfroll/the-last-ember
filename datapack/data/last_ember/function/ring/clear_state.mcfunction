# as a player: the ring's effects and modifiers off, the cooldown = half of the time worn (not less than 3 s)
attribute @s minecraft:armor modifier remove last_ember:ring_armor
attribute @s minecraft:armor_toughness modifier remove last_ember:ring_toughness
attribute @s minecraft:knockback_resistance modifier remove last_ember:ring_knockback
effect clear @s minecraft:invisibility
effect clear @s minecraft:wither
effect clear @s minecraft:darkness
effect clear @s minecraft:slowness
scoreboard players operation #w le.e = #gt le.e
scoreboard players operation #w le.e -= @s le.rt
scoreboard players operation #w le.e /= #2 le.e
execute if score #w le.e matches ..59 run scoreboard players set #w le.e 60
scoreboard players operation @s le.rcd = #gt le.e
scoreboard players operation @s le.rcd += #w le.e
scoreboard players set @s le.rpend 0
tag @s remove le.ringon
