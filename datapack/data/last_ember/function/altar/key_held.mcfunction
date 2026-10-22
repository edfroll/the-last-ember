# macro id, as the holder: remembered as the last one who held the key
scoreboard players set #kh le.alt 1
$data modify storage last_ember:keys k.$(id).h set from entity @s UUID
$data modify storage last_ember:keys k.$(id).it set value 0b
$data modify storage last_ember:keys k.$(id).got set value 1b
$data modify storage last_ember:keys k.$(id).pend set value 0b
