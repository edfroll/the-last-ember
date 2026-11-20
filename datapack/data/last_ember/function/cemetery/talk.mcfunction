# T-027: advancement reward: a player right-clicked the keeper: his window by the state of the quest (a lost shovel: he gives another)
advancement revoke @s only last_ember:cemetery/talk
scoreboard players enable @s le.ctrig
playsound minecraft:entity.villager.ambient neutral @s ~ ~ ~ 0.5 0.6
execute if score #q le.cem matches 1.. if score #sh le.cem matches 2 run function last_ember:cemetery/shovel_again
execute if score #q le.cem matches 0 run return run dialog show @s last_ember:cemetery/intro
execute if score #fv le.cem matches 1 if score #q le.cem matches 4 run return run dialog show @s last_ember:cemetery/faded_done
execute if score #fv le.cem matches 1 run return run dialog show @s last_ember:cemetery/faded
execute if score #q le.cem matches 1 run return run dialog show @s last_ember:cemetery/wait
execute if score #q le.cem matches 2..3 run return run dialog show @s last_ember:cemetery/key
execute if score #q le.cem matches 4 run return run dialog show @s last_ember:cemetery/done
