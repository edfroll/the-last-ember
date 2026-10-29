# admin: set the state {id, s} (0..6, see contract/stats)
$scoreboard players set #$(id)_s le.ct $(s)
$function last_ember:contract/gen/set_$(id)
