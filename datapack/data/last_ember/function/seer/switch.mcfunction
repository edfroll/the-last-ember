# as a seer: the other spell of the staff (its own <-> the Ashen Cover)
execute if score @s le.spsel matches 1 run return run function last_ember:seer/switch_to_0
scoreboard players set @s le.spsel 1
playsound minecraft:ui.button.click player @s ~ ~ ~ 0.6 1.6
function last_ember:seer/hint
