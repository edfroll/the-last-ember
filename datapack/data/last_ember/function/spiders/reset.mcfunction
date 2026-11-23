# T-032: admin: the thicket as in a new world (the quest of T-031 untouched): the cocoon closed with Toivo inside, his bow in the
# clearing, the Mistress alive and asleep, the elite spiders on their points, the wires, the barrels with their loot again
function last_ember:spiders/gen/cocoon_closed
scoreboard players set #toivo le.sp 0
data modify storage last_ember:spiders toivo set value 0
scoreboard players add #tgen le.sp 1
kill @e[tag=le.spt]
scoreboard players set #cuts le.sp 0
scoreboard players set #cb le.sp 0
scoreboard players set #talked le.sp 0
tag @a remove le.sptk
function last_ember:spiders/gen/bow_put
function last_ember:spiders/gen/coc_put
function last_ember:spiders/boss_reset
function last_ember:spiders/gen/dawn_all
function last_ember:spiders/gen/trip_fix_1
function last_ember:spiders/gen/trip_fix_2
function last_ember:spiders/gen/trip_fix_3
scoreboard players set #tc1 le.sp 0
scoreboard players set #tc2 le.sp 0
scoreboard players set #tc3 le.sp 0
function last_ember:spiders/gen/barrels
function last_ember:spiders/gen/props_put
tellraw @s {"text":"spiders: reset","color":"gray"}
