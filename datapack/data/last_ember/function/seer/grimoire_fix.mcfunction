# one tick after a non-seer read a grimoire: the enchanted book is taken away, the grimoire is given back
tag @s remove le.grchk
data modify storage last_ember:seer g set value {}
data modify storage last_ember:seer g.it set from entity @s Inventory[{components:{"minecraft:custom_data":{le_grimoire_res:{}}}}]
execute unless data storage last_ember:seer g.it run return 0
data modify storage last_ember:seer g.ench set from storage last_ember:seer g.it.components."minecraft:custom_data".le_grimoire_res.ench
data modify storage last_ember:seer g.lvl set from storage last_ember:seer g.it.components."minecraft:custom_data".le_grimoire_res.lvl
clear @s minecraft:enchanted_book[minecraft:custom_data~{le_grimoire_res:{}}] 1
function last_ember:seer/grimoire with storage last_ember:seer g
title @s actionbar {"text":"Письмена расплываются перед глазами","color":"gray"}
playsound minecraft:block.note_block.basedrum player @s ~ ~ ~ 0.7 0.6
