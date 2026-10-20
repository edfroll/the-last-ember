# as the resting player
function last_ember:bonfire/bind
particle minecraft:flame ~ ~1 ~ 0.4 0.4 0.4 0.01 12
playsound minecraft:block.campfire.crackle block @s ~ ~ ~ 1 1
title @s actionbar {"text":"Вы отдохнули у костра. Здесь вы возродитесь.","color":"gold"}
