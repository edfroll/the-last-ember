# as/at the stela interaction of bonfire storage last_ember:bt cur; player = @a[tag=le.clicker]
execute store result score #s le.e run data get storage last_ember:ember socket
execute if score #s le.e = @s le.bidx run return run function last_ember:ember/take
execute if entity @a[tag=le.clicker,tag=le.carrier] if items entity @a[tag=le.clicker,limit=1] weapon.mainhand *[minecraft:custom_data~{le_ember:1b}] run return run function last_ember:ember/insert
execute if entity @a[tag=le.clicker,tag=le.carrier] run return run title @a[tag=le.clicker] actionbar {"text":"Возьмите Уголь в руку, чтобы вложить его в гнездо стелы","color":"gray"}
title @a[tag=le.clicker] actionbar {"text":"Гнездо стелы пусто","color":"gray"}
