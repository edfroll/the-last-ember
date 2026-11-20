# T-026: the Crooked Fens and the Hut of the Three Witches (R1), called from last_ember:load. Blocks: tools/build/r1_fens.py (offline);
# the generated part: function/fens/gen/* (tools/build/fens_dp.py, scores explained there), dialogs dialog/fens/*, the trade windows of
# the witches (traders/fens.gen.txt -> T-017), the ambush (traps/traps.txt -> T-016). State: scores le.fn, storage last_ember:fens,
# the choice in storage last_ember:choices fens (1 Mother, 2 Maiden, 3 Crone).
scoreboard objectives add le.fn dummy
scoreboard objectives add le.fcl dummy
scoreboard objectives add le.ftk dummy
scoreboard objectives add le.fgive trigger
scoreboard players set #20 le.fn 20
function last_ember:fens/load_state
function last_ember:fens/gen/markers
schedule function last_ember:fens/loop 5t replace
