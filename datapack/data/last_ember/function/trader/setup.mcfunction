# T-017: called from last_ember:load
scoreboard objectives add le.tid dummy
function last_ember:trader/gen/init
schedule function last_ember:trader/loop 20t replace
