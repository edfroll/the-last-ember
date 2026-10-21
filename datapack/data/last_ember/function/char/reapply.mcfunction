# as a player: race modifiers were lost (respawn) -- apply again and heal to the new maximum
function last_ember:char/gen/race_apply
effect give @s minecraft:instant_health 1 10 true
