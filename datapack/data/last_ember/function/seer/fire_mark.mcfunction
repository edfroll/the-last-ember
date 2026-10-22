# as the new marker: outside the zones the fire is lit and the marker remembers when to put it out
tag @s remove le.new
function last_ember:seer/gen/zone_fire
execute if score #inz le.e matches 1 run return run kill @s
setblock ~ ~ ~ minecraft:fire
scoreboard players operation @s le.ft = #gt le.e
scoreboard players add @s le.ft 100
