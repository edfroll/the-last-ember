# T-031: admin: the state of the village
execute store result score #c le.hv if entity @e[type=minecraft:zombie_villager,tag=le.hz]
execute store result score #c2 le.hv if entity @e[type=minecraft:zombie_villager,tag=le.hza]
execute store result score #c3 le.hv if entity @e[type=minecraft:villager,tag=le.ringer]
execute store result score #q le.hv run data get storage last_ember:heather q
tellraw @s [{"text":"heather: dead villagers ","color":"gray"},{"score":{"name":"#c","objective":"le.hv"}},{"text":" (awake "},{"score":{"name":"#c2","objective":"le.hv"}},{"text":"), ringers "},{"score":{"name":"#c3","objective":"le.hv"}},{"text":", quest "},{"score":{"name":"#q","objective":"le.hv"}},{"text":", bells "},{"score":{"name":"#rang","objective":"le.hv"}}]
