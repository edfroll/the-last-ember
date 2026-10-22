# macro key: the key stays on the altar for good, every copy anywhere is void
$data modify storage last_ember:keys k.$(key).st set value 2
$function last_ember:altar/gen_bump {key:"$(key)"}
