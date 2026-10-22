$effect give @s minecraft:absorption $(d) 1 true
$execute as @a[distance=..$(r),tag=!le.caster,gamemode=!spectator] run effect give @s minecraft:absorption $(d) 0 true
$execute as @a[distance=..$(r),tag=!le.caster,gamemode=!spectator] at @s run particle minecraft:wax_on ~ ~1 ~ 0.3 0.6 0.3 0.2 12
