# as the player: inventory full, the given Ember dropped and was destroyed by the loop; socket unchanged
tag @s remove le.carrier
data remove storage last_ember:ember carrier
kill @e[type=minecraft:item,distance=..3]
title @s actionbar {"text":"Освободите место в инвентаре, чтобы взять Уголь","color":"red"}
