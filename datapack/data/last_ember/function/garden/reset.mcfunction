# T-025 TEST/ADMIN: the garden as new: 6 hearts back, awake, the key on its pedestal again (the key system: a new generation is not made
# here: use altar/reset for that), cooldowns cleared, the sensor creakings crumble, players may take the armour again
function last_ember:garden/gen/hearts_restore
scoreboard players set #key le.gd 0
data modify storage last_ember:garden key set value 0b
data modify storage last_ember:keys k.tear_creaker.got set value 0b
scoreboard players set #gcd le.gd 0
execute as @e[type=minecraft:creaking,tag=le.garden_cr] at @s run function last_ember:garden/crumble
tag @a remove le.creak_got
function last_ember:garden/gen/init
