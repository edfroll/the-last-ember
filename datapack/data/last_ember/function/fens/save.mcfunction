# T-026: the state scores -> storage (the choice is kept by fens/choose in last_ember:choices fens)
execute store result storage last_ember:fens s.vs int 1 run scoreboard players get #vs le.fn
execute store result storage last_ember:fens s.sg int 1 run scoreboard players get #sg le.fn
execute store result storage last_ember:fens s.ms int 1 run scoreboard players get #ms le.fn
execute store result storage last_ember:fens s.mt int 1 run scoreboard players get #mt le.fn
execute store result storage last_ember:fens s.sk int 1 run scoreboard players get #sk le.fn
function last_ember:fens/gen/pools_save
