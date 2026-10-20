# T-004 zones: called from last_ember:load
scoreboard objectives add le.z dummy
scoreboard players set #64 le.z 64
function last_ember:zones/gen/init
schedule function last_ember:zones/loop 1t replace
