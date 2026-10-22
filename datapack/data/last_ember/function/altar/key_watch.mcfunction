# macro id: one key, every 10 ticks
$data modify storage last_ember:keys cur set from storage last_ember:keys k.$(id)
$data modify storage last_ember:keys cur.id set value "$(id)"
function last_ember:altar/key_watch_m with storage last_ember:keys cur
