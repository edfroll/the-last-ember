# T-027: the Cemetery of the Fallen Knights and the Keeper's Lodge (R1), called from last_ember:load. Blocks: tools/build/r1_cemetery.py
# (offline); the generated part: function/cemetery/gen/* (tools/build/cemetery_dp.py, the scores explained there), dialogs
# dialog/cemetery/*, loot tables loot_table/cemetery/*, the pits and the crypt corridor (traps/traps.txt -> T-016), the zones.
scoreboard objectives add le.cem dummy
scoreboard objectives add le.ctrig trigger
scoreboard objectives add le.cbell minecraft.custom:minecraft.bell_ring
scoreboard objectives add le.cspy dummy
scoreboard objectives add le.cspc dummy
scoreboard objectives add le.chp dummy
scoreboard objectives add le.cst dummy
scoreboard players set #10 le.cem 10
scoreboard players set #20 le.cem 20
scoreboard players set #30 le.cem 30
function last_ember:cemetery/gen/init
schedule function last_ember:cemetery/loop 5t replace
