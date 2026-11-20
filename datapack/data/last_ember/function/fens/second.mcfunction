# T-026: every second (in the overworld): the witches and their talk boxes, the quest items (lost -> the quest can start again; old
# copies invalid; the items of the two other quests gone after the choice), the prices of the offended, the boats, the trails of the
# Clairvoyance
execute if score #near le.fn matches 1.. run function last_ember:fens/gen/npcs
execute if score #near le.fn matches 1.. run function last_ember:fens/gen/boats
function last_ember:fens/gen/vial
function last_ember:fens/skull
execute unless score #choice le.fn matches 0 run function last_ember:fens/purge
execute unless score #choice le.fn matches 0 if score #near le.fn matches 1.. run function last_ember:fens/gen/prices
execute as @a[gamemode=!spectator] if score @s le.fcl > #gt le.fn at @s run function last_ember:fens/gen/trails
