# T-021: region borders, chapter gates, shortcuts (called from last_ember:load)
function last_ember:gate/gen/init
scoreboard objectives add le.chx dummy
scoreboard objectives add le.chy dummy
scoreboard objectives add le.chz dummy
scoreboard objectives add le.cht dummy
scoreboard objectives add le.cnx dummy
scoreboard objectives add le.cnz dummy
scoreboard players set #5 le.gate 5
scoreboard players set #4 le.gate 4
schedule function last_ember:gate/loop 1t replace
