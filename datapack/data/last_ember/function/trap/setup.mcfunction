# T-016: called from last_ember:load
scoreboard objectives add le.tr dummy
scoreboard objectives add le.tid dummy
scoreboard objectives add le.tbud dummy
scoreboard objectives add le.chop minecraft.custom:minecraft.open_chest
scoreboard objectives add le.chopl dummy
scoreboard players set #64 le.tr 64
scoreboard players set #16 le.tr 16
scoreboard players set #10 le.tr 10
scoreboard players set #8 le.tr 8
scoreboard players set #2 le.tr 2
scoreboard players set #5 le.tr 5
scoreboard players set #20 le.tr 20
function last_ember:trap/gen/init
schedule function last_ember:trap/tick 1t replace
