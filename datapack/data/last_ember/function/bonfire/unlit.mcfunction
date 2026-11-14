# T-023: at the hearth (macro i r): the bonfire went out (the fade of its region): the look before the first lighting, smoke; lv = 0
$function last_ember:bonfire/gen/unlit_r$(r)
$data modify storage last_ember:bonfires by.b$(i).lv set value 0b
particle minecraft:large_smoke ~ ~0.6 ~ 0.3 0.4 0.3 0.02 30
particle minecraft:campfire_cosy_smoke ~ ~0.8 ~ 0.2 0.6 0.2 0.01 12
playsound minecraft:block.fire.extinguish block @a[distance=..32] ~ ~ ~ 1 0.6
