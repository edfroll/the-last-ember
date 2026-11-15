# T-024: the Enchanted Maze (R1), called from last_ember:load. Blocks: tools/build/r1_maze.py (offline: the permanent cells, the sanctum,
# the outer ring and the gate, the terrace) + templates placed here (the 6 movable cells in 3 variants, the secret exit, the 4 guards).
# State: scores le.mz (see tools/build/maze_dp.py) mirrored in storage last_ember:maze {v:{c1..c6}, key, exit}.
scoreboard objectives add le.mz dummy
scoreboard objectives add le.mzs dummy
scoreboard objectives add le.mzg dummy
scoreboard players set #24 le.mz 24
scoreboard players set #20 le.mz 20
function last_ember:maze/gen/init
function last_ember:maze/gen/markers
schedule function last_ember:maze/loop 5t replace
