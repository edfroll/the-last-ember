# any player at this bonfire takes the Ember out of the socket (fails without a free slot)
execute as @a[tag=le.clicker,limit=1] run function last_ember:ember/give
execute as @a[tag=le.clicker,limit=1] unless function last_ember:ember/has run return run function last_ember:ember/take_failed
data modify storage last_ember:ember socket set value -1
kill @e[type=minecraft:item_display,tag=le.ember_disp]
playsound minecraft:block.respawn_anchor.deplete block @a[distance=..16] ~ ~ ~ 0.8 1.4
title @a[tag=le.clicker] actionbar {"text":"Теперь Уголь несёте вы.","color":"gold"}
