# knight blocked a melee hit with the shield: the attacker takes 25% of the blocked damage (50% with the Guardian's Shield, T-019) (bucket 5: 5 damage, armor does not reduce it), not less than 1
advancement revoke @s only last_ember:knight/block_5
execute unless entity @s[tag=le.class.knight] run return 0
tag @s add le.ref
execute if items entity @s weapon.* minecraft:shield[minecraft:custom_data~{le_guard:1b}] on attacker run damage @s 10 minecraft:magic by @a[tag=le.ref,limit=1]
execute unless items entity @s weapon.* minecraft:shield[minecraft:custom_data~{le_guard:1b}] on attacker run damage @s 5 minecraft:magic by @a[tag=le.ref,limit=1]
execute on attacker run particle minecraft:crit ~ ~1 ~ 0.3 0.3 0.3 0.2 8
tag @s remove le.ref
