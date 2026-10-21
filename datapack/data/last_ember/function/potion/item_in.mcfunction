# as an item entity inside a cauldron (the cauldron is the entity with the tag le.cur): an ingredient from a healer is taken, anything else is pushed out
execute if entity @e[type=minecraft:interaction,tag=le.cur,scores={le.cstate=1},limit=1,distance=..2] run return run function last_ember:potion/eject
scoreboard players set #h le.e 0
execute on origin if entity @s[tag=le.class.healer] run scoreboard players set #h le.e 1
execute if score #h le.e matches 0 run return run function last_ember:potion/eject
function last_ember:potion/ingredient
execute if score #bit le.e matches 0 run return run function last_ember:potion/eject
execute if score #bit le.e matches 1048576 if data entity @s Item.components."minecraft:custom_data".le_mod run return run function last_ember:potion/eject
data modify storage last_ember:cauldron cur set from entity @s Item
scoreboard players set #acc le.e 0
execute as @e[type=minecraft:interaction,tag=le.cur,limit=1,distance=..2] store result score #acc le.e run function last_ember:potion/try_add
execute if score #acc le.e matches 0 run return run function last_ember:potion/eject
particle minecraft:splash ~ ~0.2 ~ 0.2 0.1 0.2 0.1 12
playsound minecraft:entity.generic.splash block @a[distance=..12] ~ ~ ~ 0.6 1.2
execute store result score #c le.e run data get entity @s Item.count
scoreboard players remove #c le.e 1
execute if score #c le.e matches ..0 run return run kill @s
execute store result entity @s Item.count int 1 run scoreboard players get #c le.e
function last_ember:potion/eject
