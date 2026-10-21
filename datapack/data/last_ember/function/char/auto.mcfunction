# TEST/DEV: with `scoreboard players set #autochar le.e 1` (old T-004..T-007 tests) newcomers skip the Hall: a silent people+class (no tags, no kit),
# bound to the start bonfire at once, no teleport
scoreboard players set @s le.race 1
scoreboard players set @s le.class 1
tag @s add le.kit
function last_ember:char/gen/race_apply_1
function last_ember:char/gen/class_apply_1
function last_ember:bonfire/bind_start
