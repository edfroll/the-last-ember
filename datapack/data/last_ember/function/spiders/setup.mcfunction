# T-032: the Spider Thicket (R1), called from last_ember:load. Blocks: tools/build/r1_spiders.py (offline); the generated part:
# function/spiders/gen/* (tools/build/spiders_dp.py, the scores explained there), dialogs dialog/spiders/*, the templates
# structure/spiders/*.nbt, the zones spiders_nest (no_spawn) and spiders_cocoon; the fire ban of the place (zones/nofire.txt: the staffs;
# spiders/fire: fire, lava and lit campfires round the players in the place). No fading of its own (the common fading of chapter I).
scoreboard objectives add le.sp dummy
scoreboard objectives add le.spn dummy
scoreboard objectives add le.spg dummy
scoreboard objectives add le.spbg dummy
scoreboard objectives add le.sptg dummy
scoreboard objectives add le.spwt dummy
scoreboard objectives add le.spfight dummy
scoreboard objectives add le.spwin dummy
scoreboard objectives add le.sptrig trigger
execute unless data storage last_ember:spiders boss run data modify storage last_ember:spiders boss set value 0
execute unless data storage last_ember:spiders toivo run data modify storage last_ember:spiders toivo set value 0
execute store result score #boss le.sp run data get storage last_ember:spiders boss
execute store result score #toivo le.sp run data get storage last_ember:spiders toivo
function last_ember:spiders/gen/init
scoreboard players set #24000 le.sp 24000
schedule function last_ember:spiders/loop 5t replace
