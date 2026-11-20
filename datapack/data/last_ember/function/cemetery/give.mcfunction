# T-027: macro key: give the quest item <key> to @s with its current generation
data modify storage last_ember:cemetery tmp set value {gen:1}
$data modify storage last_ember:cemetery tmp.gen set from storage last_ember:cemetery gen.$(key)
$function last_ember:cemetery/gen/give_$(key) with storage last_ember:cemetery tmp
