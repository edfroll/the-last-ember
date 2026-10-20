# as/at the carrier who lost the Ember (still a carrier: only a stela can take that role away)
function last_ember:ember/bump_gen
execute as @e[type=#last_ember:item_holders,distance=..10] run function last_ember:ember/strip_entity
scoreboard players set #rn le.e 0
execute anchored eyes positioned ^ ^ ^ run function last_ember:ember/ray
function last_ember:ember/strip_enderchest
function last_ember:ember/give
title @s actionbar {"text":"Уголь не покидает Несущего. Передать его можно только у костра.","color":"gold"}
playsound minecraft:block.fire.extinguish player @s ~ ~ ~ 0.6 1.6
