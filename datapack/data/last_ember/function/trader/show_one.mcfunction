$data modify storage last_ember:trader r set from entity @s Offers.Recipes[$(i)]
execute store result score #mx le.tr run data get storage last_ember:trader r.maxUses
execute store result score #us le.tr run data get storage last_ember:trader r.uses
scoreboard players operation #mx le.tr -= #us le.tr
tellraw @a[tag=le.stk] [{"text":"  ","color":"gray"},{"storage":"last_ember:trader","nbt":"r.sell.id"},{"text":" x"},{"storage":"last_ember:trader","nbt":"r.sell.count"},{"text":": осталось "},{"score":{"name":"#mx","objective":"le.tr"}},{"text":" из "},{"storage":"last_ember:trader","nbt":"r.maxUses"}]
