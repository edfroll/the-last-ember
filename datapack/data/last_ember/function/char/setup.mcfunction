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
scoreboard players set #200 le.e 200
scoreboard players set #6 le.e 6
scoreboard objectives add le.dtk minecraft.custom:minecraft.damage_taken
scoreboard objectives add le.dlast dummy
scoreboard objectives add le.hurtcd dummy
scoreboard objectives add le.bless dummy
scoreboard objectives add le.blday dummy
scoreboard objectives add le.sat dummy
scoreboard objectives add le.satcd dummy
scoreboard players set #24000 le.e 24000
scoreboard players set #6667 le.e 6667
scoreboard players set #8 le.e 8
scoreboard objectives add le.immune dummy
scoreboard objectives add le.amcd dummy
function last_ember:potion/consts
scoreboard objectives add le.cmask dummy
scoreboard objectives add le.cstate dummy
scoreboard objectives add le.ctimer dummy
scoreboard objectives add le.crec dummy
scoreboard objectives add le.ctier dummy
scoreboard objectives add le.cbase dummy
scoreboard players set #100 le.e 100
