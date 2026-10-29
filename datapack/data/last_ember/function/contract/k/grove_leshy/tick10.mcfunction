function last_ember:contract/m/tick10
# the hollow in its back glows (seen from behind)
execute if score @s le.ls matches 2 rotated as @s rotated ~ 0 run particle minecraft:dust{color:[1.0,0.6,0.15],scale:0.9} ^ ^3.2 ^-0.75 0.1 0.2 0.1 0 2
