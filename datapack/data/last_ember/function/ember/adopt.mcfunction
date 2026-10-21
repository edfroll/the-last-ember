# as a non-carrier holding a valid Ember: becomes the carrier only if there is none and the socket is empty; else it is taken away
execute store result score #s le.e run data get storage last_ember:ember socket
execute if entity @a[tag=le.carrier] run return run clear @s *[minecraft:custom_data~{le_ember:1b}]
execute unless score #s le.e matches -1 run return run clear @s *[minecraft:custom_data~{le_ember:1b}]
tag @s add le.carrier
data modify storage last_ember:ember carrier set from entity @s UUID
