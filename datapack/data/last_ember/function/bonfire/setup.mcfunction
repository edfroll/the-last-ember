# T-005: called from last_ember:load
scoreboard objectives add le.e dummy
scoreboard objectives add le.bidx dummy
scoreboard objectives add le.sx dummy
scoreboard objectives add le.sy dummy
scoreboard objectives add le.sz dummy
scoreboard objectives add le.sd dummy
scoreboard objectives add le.sb dummy
execute unless data storage last_ember:bonfires by run data modify storage last_ember:bonfires by set value {}
execute unless data storage last_ember:ember gen run data merge storage last_ember:ember {gen:0,socket:-1}
function last_ember:bonfire/gen/register
function last_ember:bonfire/gen/start
schedule function last_ember:ember/loop 1t replace
schedule function last_ember:bonfire/spawn_loop 20t replace
