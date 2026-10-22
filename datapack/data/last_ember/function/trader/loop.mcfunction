# every second: traders that stand in loaded chunks are put in place; a trader that was moved goes back and off any vehicle
function last_ember:trader/gen/build_pending
function last_ember:trader/gen/hold
schedule function last_ember:trader/loop 20t replace
