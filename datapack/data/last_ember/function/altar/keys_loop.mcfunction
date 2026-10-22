# every 10 ticks: uniqueness of the keys
function last_ember:altar/gen/keys_watch
schedule function last_ember:altar/keys_loop 10t replace
