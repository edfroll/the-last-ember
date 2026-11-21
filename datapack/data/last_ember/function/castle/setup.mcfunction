# T-028: the approaches to the Enchanted Castle (R1), called from last_ember:load. Blocks: tools/build/r1_castle.py (offline); the generated
# part: function/castle/gen/* (tools/build/castle_dp.py, the scores explained there), the zones castle / castle_rock_* (zones/zones.txt),
# the damage type last_ember:colossus (through armour, enchantments, resistance, shields; no knockback: the flight is ours).
scoreboard objectives add le.cas dummy
scoreboard objectives add le.cw dummy
scoreboard objectives add le.cf dummy
scoreboard objectives add le.cg dummy
scoreboard objectives add le.co dummy
scoreboard objectives add le.ck dummy
scoreboard objectives add le.csx dummy
scoreboard objectives add le.csy dummy
scoreboard objectives add le.csz dummy
scoreboard objectives add le.cex dummy
scoreboard objectives add le.cey dummy
scoreboard objectives add le.cez dummy
scoreboard players set #N le.cas 24
scoreboard players set #3 le.cas 3
scoreboard players set #4 le.cas 4
scoreboard players set #20 le.cas 20
function last_ember:castle/gen/init
schedule function last_ember:castle/loop 5t replace
