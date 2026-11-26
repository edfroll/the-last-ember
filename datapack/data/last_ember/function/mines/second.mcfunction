# T-033: every second (in the overworld, players near the mines): the difficulty, the game time, the old generations, the points of the
# dead miners (alive / killed / back 20 min later), the awake ones home when nobody is within 32, the resting ones knock now and then
# (block.stone.hit: miners within 16, Bran within 20 - heard through the big collapse), Bran (peaceful: his things in the pocket; missing,
# dead, his leash), the carts, the props
scoreboard players set #t le.mn 0
function last_ember:mines/gen/near
execute if score #near le.mn matches 0 run return 0
execute store result score #df le.mn run difficulty
execute store result score #gt le.mn run time query gametime
execute if score #df le.mn matches 0 run function last_ember:mines/gen/forget
execute if score #df le.mn matches 0 if score #bran le.mn matches 0..1 run function last_ember:mines/gen/bran_peace
execute as @e[type=minecraft:zombie,tag=le.mn_dead] run function last_ember:mines/gen/genchk
function last_ember:mines/gen/points
execute as @e[type=minecraft:zombie,tag=le.mna] at @s unless entity @e[type=minecraft:player,gamemode=!spectator,distance=..32] run function last_ember:mines/rest
execute as @e[type=minecraft:zombie,tag=le.mn_dead,tag=le.mnr] run function last_ember:mines/knock_dead
execute if score #bran le.mn matches 0 as @e[type=minecraft:zombie,tag=le.mn_bran,tag=le.mnr] run function last_ember:mines/knock
execute if score #df le.mn matches 1.. run function last_ember:mines/gen/bran_check
function last_ember:mines/gen/carts
function last_ember:mines/gen/props_check
