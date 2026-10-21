# T-009: called from last_ember:load. Races, classes, pads of the Hall of Awakening.
scoreboard objectives add le.race dummy
scoreboard objectives add le.class dummy
scoreboard objectives add le.tier dummy
scoreboard objectives add le.pid dummy
scoreboard objectives add le.pend dummy
scoreboard objectives add le.pendt dummy
scoreboard objectives add le.swcd dummy
scoreboard objectives add le.hp dummy
execute unless data storage last_ember:char built run data modify storage last_ember:char built set value {}
execute in minecraft:overworld run setworldspawn 0 58 -8
schedule function last_ember:char/loop 1t replace
scoreboard players set #10 le.e 10
