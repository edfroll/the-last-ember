# T-027: every second (in the overworld): the keeper and his dog, the click boxes, the graves, the quest items, the bell, the unrest,
# the spirits, the curses, the crypt, the fading
scoreboard players add #sec le.cem 1
scoreboard players enable @a le.ctrig
function last_ember:cemetery/gen/near
scoreboard players set #kp le.cem 0
execute if predicate last_ember:night run scoreboard players set #kp le.cem 1
execute if score #fv le.cem matches 1 run scoreboard players set #kp le.cem 2
execute if score #near le.cem matches 1.. run function last_ember:cemetery/gen/npcs
execute if score #near le.cem matches 1.. run function last_ember:cemetery/gen/boxes
execute if score #near le.cem matches 1.. run function last_ember:cemetery/gen/graves
function last_ember:cemetery/gen/key
function last_ember:cemetery/items
execute as @a[scores={le.cbell=1..}] at @s run function last_ember:cemetery/bell
function last_ember:cemetery/unrest
function last_ember:cemetery/gen/spirits_check
execute as @e[tag=le.cspirit] at @s run function last_ember:cemetery/spirit_sec
execute as @a[gamemode=!spectator] run function last_ember:cemetery/curse
execute if score #near le.cem matches 1.. run function last_ember:cemetery/crypt
function last_ember:cemetery/gen/fade_sync
