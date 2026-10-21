# knight blocked a melee hit with the shield: the attacker takes 25% of the blocked damage (bucket 4: 4 damage, armor does not reduce it), not less than 1
advancement revoke @s only last_ember:knight/block_4
execute unless entity @s[tag=le.class.knight] run return 0
tag @s add le.ref
execute on attacker run damage @s 4 minecraft:magic by @a[tag=le.ref,limit=1]
execute on attacker run particle minecraft:crit ~ ~1 ~ 0.3 0.3 0.3 0.2 8
tag @s remove le.ref
