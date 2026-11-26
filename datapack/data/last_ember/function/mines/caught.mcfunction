# T-033: as/at a player in the zone of a falling cave-in: hurt up to 2 hearts but never under one (trap/shield of T-016), slowness 2 s;
# pushed out by the caller
tag @s add le.mncaught
function last_ember:trap/shield
damage @s 4 minecraft:falling_block
effect give @s minecraft:slowness 2 1 true
scoreboard players add #caught le.mn 1
