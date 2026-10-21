# healer + sneaking + cauldron in hand at a burning hearth: the cauldron goes over the fire (everyone else: the usual click)
execute if data storage last_ember:bt cur{state:1} as @a[tag=le.clicker,tag=le.class.healer,predicate=last_ember:sneaking] if items entity @s weapon.mainhand *[minecraft:custom_data~{le_cauldron:1b}] run return run function last_ember:bonfire/cauldron_put
execute if data storage last_ember:bt cur{state:1} as @a[tag=le.clicker] at @s run function last_ember:bonfire/rest
execute unless data storage last_ember:bt cur{state:1} if entity @a[tag=le.clicker,tag=le.carrier] run function last_ember:bonfire/light
execute unless data storage last_ember:bt cur{state:1} unless entity @a[tag=le.clicker,tag=le.carrier] run title @a[tag=le.clicker] actionbar {"text":"Зажечь костёр может только Несущий Уголь","color":"gray"}
