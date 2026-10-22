# macro id: the key was lying on the floor and is gone (lava, fire, cactus, void, despawn, explosion): a new generation is owed to the last holder
$data modify storage last_ember:keys k.$(id).it set value 0b
$function last_ember:altar/gen_bump {key:"$(id)"}
$data modify storage last_ember:keys k.$(id).pend set value 1b
