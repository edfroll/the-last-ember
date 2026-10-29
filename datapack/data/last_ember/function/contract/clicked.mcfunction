# advancement reward: a player right-clicked a box in front of a board sign
advancement revoke @s only last_ember:contract/click
tag @s add le.clicker
scoreboard players add #clicks le.ct 1
scoreboard players set #slot le.ct 0
execute as @e[type=minecraft:interaction,tag=le.cboard,distance=..8] if function last_ember:bonfire/is_mine run scoreboard players operation #slot le.ct = @s le.cslot
execute as @e[type=minecraft:interaction,tag=le.cboard,distance=..8] if function last_ember:bonfire/is_mine run data remove entity @s interaction
tag @s remove le.clicker
execute if score #slot le.ct matches 1.. run function last_ember:contract/gen/click
playsound minecraft:item.book.page_turn player @s ~ ~ ~ 0.6 1
