# as a player: function last_ember:char/set_tier {tier:0..6} -- the tier changes (altars of the chapters, later); the class modifiers and effects are re-applied
$scoreboard players set @s le.tier $(tier)
effect clear @s minecraft:resistance
function last_ember:char/gen/class_apply
function last_ember:char/effects
