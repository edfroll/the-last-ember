# ADMIN/TEST: function last_ember:maze/reset: the key back on its pedestal (only if nobody has it yet), the guards stone, the exit closed,
# all the movable cells in variant 1, the dead-end heads straight
execute if data storage last_ember:keys k.thread_labyrinth{got:0b} run scoreboard players set #key le.mz 0
execute if data storage last_ember:keys k.thread_labyrinth{got:0b} run data modify storage last_ember:maze key set value 0
scoreboard players set #exit le.mz 0
data modify storage last_ember:maze exit set value 0
scoreboard players set #shuf le.mz 0
scoreboard players set #gcd le.mz 0
execute in minecraft:overworld run function last_ember:maze/gen/reset_guards
function last_ember:maze/set {cell:1,var:1}
function last_ember:maze/set {cell:2,var:1}
function last_ember:maze/set {cell:3,var:1}
function last_ember:maze/set {cell:4,var:1}
function last_ember:maze/set {cell:5,var:1}
function last_ember:maze/set {cell:6,var:1}
execute in minecraft:overworld run function last_ember:maze/gen/sync_exit
execute in minecraft:overworld run function last_ember:maze/heads_reset
