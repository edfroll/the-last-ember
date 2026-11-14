# every second: when the Circle's chunks are loaded: the inscriptions once, the templates follow the altar (not during the event)
schedule function last_ember:weepers/sec 20t replace
execute in minecraft:overworld unless function last_ember:weepers/gen/loaded run return 0
execute in minecraft:overworld unless data storage last_ember:weepers {built:1b} run function last_ember:weepers/gen/labels
execute if data storage last_ember:altars a.weepers{ev:-1} in minecraft:overworld run function last_ember:weepers/sync
