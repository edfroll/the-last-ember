# T-030: every second (in the overworld, a player near the grove or near the Circle point): where the Advisor should be (day: the
# armchair, night: the observatory, every key of chapter I taken and the chapter not done: the west arch of the Circle), the move (only
# when nobody is within 12 of the old and the new point), doubles and the missing, the smoke of the pipe (every 2 s), the decor once
scoreboard players set #t le.grv 0
scoreboard players add #sec le.grv 1
scoreboard players enable @a le.atrig
execute as @e[tag=le.advent] unless score @s le.agen = #agen le.grv run kill @s
function last_ember:grove/gen/near
execute if score #near le.grv matches 0 run return 0
scoreboard players set #ap le.grv 0
execute if predicate last_ember:grove/night run scoreboard players set #ap le.grv 1
function last_ember:grove/gen/circle_rule
execute if score #pin le.grv matches 1 run return 0
execute unless score #ap le.grv = #cur le.grv run function last_ember:grove/gen/try_move
function last_ember:grove/gen/check_here
function last_ember:grove/gen/deco_check
scoreboard players operation #s2 le.grv = #sec le.grv
scoreboard players operation #s2 le.grv %= #2 le.grv
execute if score #s2 le.grv matches 0 run function last_ember:grove/gen/smoke
