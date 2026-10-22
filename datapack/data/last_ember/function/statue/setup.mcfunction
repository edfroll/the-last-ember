# T-016: called from last_ember:load
scoreboard objectives add le.st dummy
scoreboard objectives add le.sid dummy
scoreboard players set #20 le.st 20
scoreboard players set #5 le.st 5
function last_ember:statue/gen/init
schedule function last_ember:statue/tick 1t replace
