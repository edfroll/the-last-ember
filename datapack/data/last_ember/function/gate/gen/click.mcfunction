# generated: as the interaction of a shortcut that was clicked (le.scw = region number), @a[tag=le.scclicker] = the player
execute if entity @s[tag=le.schub] run return run title @a[tag=le.scclicker] actionbar {"text": "Заперто с той стороны.", "color": "gray"}
title @a[tag=le.scclicker] actionbar {"text": "Заперто.", "color": "gray"}
