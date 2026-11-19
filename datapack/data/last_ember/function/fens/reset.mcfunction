# T-026: ADMIN/TEST: the fens as in a new game: no choice, the quest items gone, the vial back in the chest (the ambush is set again),
# the heads open, the Master in the gap, the prices back, the intros unheard, the Call of the Ember leads to the table again
scoreboard players set #choice le.fn 0
data modify storage last_ember:choices fens set value 0
clear @a *[minecraft:custom_data~{le_citem:"fens_vial"}]
clear @a *[minecraft:custom_data~{le_citem:"fens_sedge"}]
clear @a *[minecraft:custom_data~{le_citem:"fens_skull"}]
kill @e[type=minecraft:item,nbt={Item:{components:{"minecraft:custom_data":{le_citem:"fens_vial"}}}}]
function last_ember:fens/gen/vial_unchest
execute store result score #g le.fn run data get storage last_ember:fens vial.gen
scoreboard players add #g le.fn 1
execute store result storage last_ember:fens vial.gen int 1 run scoreboard players get #g le.fn
scoreboard players set #vs le.fn 0
scoreboard players set #sg le.fn 0
scoreboard players set #sk le.fn 0
execute as @e[type=minecraft:drowned,tag=le.fmaster] at @s run tp @s ~ ~-300 ~
kill @e[type=minecraft:drowned,tag=le.fmaster]
scoreboard players set #ms le.fn 0
function last_ember:fens/gen/heads_kill
function last_ember:fens/gen/count
function last_ember:fens/gen/prices_base_1
function last_ember:fens/gen/prices_base_2
function last_ember:fens/gen/prices_base_3
tag @a remove le.fh1
tag @a remove le.fh2
tag @a remove le.fh3
data modify storage last_ember:keys k.crown_witches.got set value 0b
function last_ember:trap/reset {id:"fens_ambush"}
function last_ember:fens/save
