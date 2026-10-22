# the blink has no room: a dull sound and a line over the hotbar, the cooldown is kept
kill @e[type=marker,tag=le.ray]
tag @s remove le.caster
playsound minecraft:block.note_block.basedrum player @s ~ ~ ~ 0.7 0.6
title @s actionbar {"text":"Нет места","color":"gray"}
return 0
