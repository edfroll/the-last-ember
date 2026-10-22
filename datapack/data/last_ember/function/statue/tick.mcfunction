# every tick: the statues that are waking up; every 5 ticks the wake-up checks; every second the pedestals, the return of the awake ones, the cooldowns
function last_ember:statue/gen/tick
scoreboard players add #t le.st 1
scoreboard players operation #t5 le.st = #t le.st
scoreboard players operation #t5 le.st %= #5 le.st
execute if score #t5 le.st matches 0 run function last_ember:statue/gen/check
scoreboard players operation #t20 le.st = #t le.st
scoreboard players operation #t20 le.st %= #20 le.st
execute if score #t20 le.st matches 0 run function last_ember:statue/second
schedule function last_ember:statue/tick 1t replace
