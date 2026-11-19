# T-025: the Garden of Silence (R1), called from last_ember:load. Blocks: tools/build/r1_garden.py (offline: relief, pale oaks, the
# 6 living hearts, the 12 carved faces, the orangery, the gardener's house, the path, 10 sculk sensors, eyeblossoms). State: scores le.gd
# (see tools/build/garden_dp.py) mirrored in storage last_ember:garden {h:{h1..h6}, asleep, key}. The Creaking armour: function/creak/.
scoreboard objectives add le.gd dummy
scoreboard objectives add le.gdt dummy
scoreboard players set #20 le.gd 20
scoreboard players set #100 le.gd 100
function last_ember:garden/gen/init
function last_ember:garden/gen/markers
schedule function last_ember:garden/loop 5t replace
