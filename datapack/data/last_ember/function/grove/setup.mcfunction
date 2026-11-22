# T-030: the Mushroom Grove of the Advisor (R1), called from last_ember:load. Blocks: tools/build/r1_grove.py (offline); the generated
# part: function/grove/gen/* (tools/build/grove_dp.py, the scores explained there), dialogs dialog/grove/*, the face templates
# structure/grove/face_<k>_closed|open.nbt, the zone `grove` (no_spawn). The grove never fades (regions/fade.txt has no line for it).
scoreboard objectives add le.grv dummy
scoreboard objectives add le.agen dummy
scoreboard objectives add le.ametg dummy
scoreboard objectives add le.atrig trigger
execute unless score #agen le.grv = #agen le.grv run scoreboard players set #agen le.grv 0
execute unless score #cur le.grv = #cur le.grv run scoreboard players set #cur le.grv -1
execute unless score #met le.grv = #met le.grv run scoreboard players set #met le.grv 0
execute unless score #pin le.grv = #pin le.grv run scoreboard players set #pin le.grv 0
scoreboard players set #miss le.grv 0
scoreboard players set #2 le.grv 2
schedule function last_ember:grove/loop 5t replace
