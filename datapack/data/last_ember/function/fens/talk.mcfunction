# T-026: advancement reward: a player right-clicked the thing of a witch (the Mother's cauldron, the Maiden's mirror, the Crone's cage):
# her window. After the choice: her thanks or her offence; the first talk of this player: her introduction; then the give button when
# the task is done (the Maiden: all 5 heads closed), else her "not yet"
advancement revoke @s only last_ember:fens/talk
scoreboard players add @s le.ftk 1
function last_ember:fens/gen/talk_which
execute if score #k le.fn matches 0 run return 0
playsound minecraft:entity.witch.ambient neutral @s ~ ~ ~ 0.7 0.9
execute if score #choice le.fn = #k le.fn if score #k le.fn matches 1 run return run dialog show @s last_ember:fens/thanks_1
execute if score #choice le.fn = #k le.fn if score #k le.fn matches 2 run return run dialog show @s last_ember:fens/thanks_2
execute if score #choice le.fn = #k le.fn if score #k le.fn matches 3 run return run dialog show @s last_ember:fens/thanks_3
execute unless score #choice le.fn matches 0 if score #k le.fn matches 1 run return run dialog show @s last_ember:fens/offended_1
execute unless score #choice le.fn matches 0 if score #k le.fn matches 2 run return run dialog show @s last_ember:fens/offended_2
execute unless score #choice le.fn matches 0 if score #k le.fn matches 3 run return run dialog show @s last_ember:fens/offended_3
execute if score #k le.fn matches 1 run return run function last_ember:fens/talk_1
execute if score #k le.fn matches 2 run return run function last_ember:fens/talk_2
execute if score #k le.fn matches 3 run return run function last_ember:fens/talk_3
