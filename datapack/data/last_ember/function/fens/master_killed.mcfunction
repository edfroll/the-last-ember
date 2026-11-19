# T-026: advancement reward: a player killed the Master of the Causeway. Before the choice and while no skull is out: the skull goes to
# the killer (its current generation; once: the Master stays down while the skull is in the game). Otherwise (the Crone offended, or the
# skull already given) he is a common elite and comes back in 10 minutes.
advancement revoke @s only last_ember:fens/master
execute if score #choice le.fn matches 0 if score #sk le.fn matches 0 run return run function last_ember:fens/skull_give
scoreboard players set #ms le.fn 3
scoreboard players operation #mt le.fn = #gt le.fn
scoreboard players add #mt le.fn 12000
function last_ember:fens/save
