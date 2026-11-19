# T-025: every second (in the overworld): the hearts are counted, the faces follow the night, the sensor creakings crumble in time
# (60 s, nobody near, more than 6 creakings in the garden), the locked door stays shut, the key and the stand stand
function last_ember:garden/gen/hearts
function last_ember:garden/gen/faces
execute as @e[type=minecraft:creaking,tag=le.garden_cr] if score #gt le.gd >= @s le.gdt at @s run function last_ember:garden/crumble
function last_ember:garden/gen/away
execute if entity @e[type=minecraft:creaking,tag=le.garden_cr,limit=1] run function last_ember:garden/limit
function last_ember:garden/gen/door_check
function last_ember:garden/gen/key_check
function last_ember:garden/gen/stand_check
