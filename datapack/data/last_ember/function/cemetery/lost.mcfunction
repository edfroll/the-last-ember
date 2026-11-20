# T-027: macro key, state, to: old copies of the quest item go; when no copy is held by a player in the game and none lies on the
# ground, the state score #<state> becomes <to> and the generation grows (the old copies of the absent players become invalid)
$data modify storage last_ember:cemetery tmp set value {key:"$(key)"}
$data modify storage last_ember:cemetery tmp.gen set from storage last_ember:cemetery gen.$(key)
function last_ember:fens/invalid with storage last_ember:cemetery tmp
function last_ember:fens/count with storage last_ember:cemetery tmp
execute if score #c le.fn matches 1.. run return 0
$scoreboard players set #$(state) le.cem $(to)
$execute store result score #g le.cem run data get storage last_ember:cemetery gen.$(key)
scoreboard players add #g le.cem 1
$execute store result storage last_ember:cemetery gen.$(key) int 1 run scoreboard players get #g le.cem
function last_ember:cemetery/save
