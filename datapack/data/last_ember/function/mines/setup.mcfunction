# T-033: the Iron Ore Mines (R1), called from last_ember:load. Blocks: tools/build/r1_mines.py (offline); the generated part:
# function/mines/gen/* (tools/build/mines_dp.py, the scores explained there), the templates structure/mines/cave_<n>_before|after.nbt,
# the zone mines_headframe (adventure). The mines are breakable (HQ T-033, 3); no bonfire of their own.
scoreboard objectives add le.mn dummy
scoreboard objectives add le.mnk dummy
scoreboard objectives add le.mng dummy
scoreboard objectives add le.mnt dummy
execute unless data storage last_ember:mines caves run data modify storage last_ember:mines caves set value {c1:0,c2:0,c3:0}
execute unless data storage last_ember:mines bran run data modify storage last_ember:mines bran set value 0
function last_ember:mines/gen/init
schedule function last_ember:mines/loop 5t replace
