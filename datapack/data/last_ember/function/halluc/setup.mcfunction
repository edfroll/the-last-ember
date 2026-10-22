# T-015: called from last_ember:load
scoreboard objectives add le.h dummy
scoreboard objectives add le.rest minecraft.custom:minecraft.time_since_rest
scoreboard objectives add le.hstg dummy
scoreboard objectives add le.hw dummy
scoreboard objectives add le.hsh dummy
scoreboard objectives add le.hfm dummy
scoreboard objectives add le.hpu dummy
scoreboard objectives add le.hk dummy
scoreboard objectives add le.hst dummy
scoreboard objectives add le.hid dummy
scoreboard players set #20 le.h 20
scoreboard players set #360 le.h 360
scoreboard players set #sh_on le.h 1
gamerule players_sleeping_percentage 50
schedule function last_ember:halluc/loop 20t replace
schedule function last_ember:halluc/frames 4t replace
