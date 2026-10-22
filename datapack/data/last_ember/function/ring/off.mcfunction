# as a wearer: the ring is off (taken off, thrown out, stolen): the armor comes back, everything is as before the ring
scoreboard players set #dd le.e 0
function last_ember:ring/restore_armor
function last_ember:ring/clear_state
playsound minecraft:item.armor.equip_leather player @s ~ ~ ~ 0.3 0.8
