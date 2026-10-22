# as the carrier who pressed Shift + F: the hands are swapped back (the Ember to the main hand, the other item to the off hand), then the Call
execute at @s run summon minecraft:armor_stand ~ ~ ~ {Marker:1b,Invisible:1b,NoGravity:1b,Silent:1b,Tags:["le.swapstand"]}
item replace entity @e[type=minecraft:armor_stand,tag=le.swapstand,limit=1,sort=nearest,distance=..2] weapon.mainhand from entity @s weapon.offhand
item replace entity @s weapon.offhand from entity @s weapon.mainhand
item replace entity @s weapon.mainhand from entity @e[type=minecraft:armor_stand,tag=le.swapstand,limit=1,sort=nearest,distance=..2] weapon.mainhand
kill @e[type=minecraft:armor_stand,tag=le.swapstand,distance=..2]
execute if score #gt le.e < @s le.ecd run return run function last_ember:altar/call_wait
scoreboard players operation @s le.ecd = #gt le.e
scoreboard players add @s le.ecd 1200
function last_ember:altar/call_run
