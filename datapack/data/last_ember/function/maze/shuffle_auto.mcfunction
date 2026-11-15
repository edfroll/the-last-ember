# T-024: 45 s with players in the maze: 1..2 random free movable cells rebuild into another variant
scoreboard players set #shuf le.mz 0
execute store result score #want le.mz run random value 1..2
execute store result score #r le.mz run random value 1..6
function last_ember:maze/gen/round
