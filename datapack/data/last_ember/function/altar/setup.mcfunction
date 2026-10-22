# T-013: called from last_ember:load
scoreboard objectives add le.alt dummy
scoreboard objectives add le.pid dummy
scoreboard objectives add le.ecd dummy
scoreboard objectives add le.eslast dummy
execute unless score #chapters le.alt matches 0.. run scoreboard players set #chapters le.alt 0
scoreboard players set #5 le.alt 5
# 1 = the tier of everybody follows the chapters (the game); 0 = the tests set tiers by hand
execute unless score #tiersync le.alt matches 0..1 run scoreboard players set #tiersync le.alt 1
execute unless data storage last_ember:altars a run data modify storage last_ember:altars a set value {}
execute unless data storage last_ember:altars p run data modify storage last_ember:altars p set value {}
execute unless data storage last_ember:keys k run data modify storage last_ember:keys k set value {}
function last_ember:altar/gen/register
schedule function last_ember:altar/tick 1t replace
schedule function last_ember:altar/loop 20t replace
schedule function last_ember:altar/keys_loop 10t replace
schedule function last_ember:altar/ember_loop 5t replace
