# macro key: the current generation +1 (every older copy becomes void)
$execute store result score #g le.alt run data get storage last_ember:keys k.$(key).gen
scoreboard players add #g le.alt 1
$execute store result storage last_ember:keys k.$(key).gen int 1 run scoreboard players get #g le.alt
