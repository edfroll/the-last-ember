# macro id, as an online player: the key owed to him comes back into the inventory (also when he was offline when it was lost)
$execute unless data storage last_ember:keys k.$(id){pend:1b} run return 0
$data modify storage last_ember:keys tmp set from storage last_ember:keys k.$(id).h
execute store success score #d le.alt run data modify storage last_ember:keys tmp set from entity @s UUID
execute if score #d le.alt matches 1 run return 0
$data modify storage last_ember:keys k.$(id).pend set value 0b
$function last_ember:altar/gen/give_dispatch {id:"$(id)"}
title @s actionbar {"text":"Ключ вернулся к тебе","color":"light_purple"}
playsound minecraft:block.amethyst_block.chime player @s ~ ~ ~ 1 1.2
