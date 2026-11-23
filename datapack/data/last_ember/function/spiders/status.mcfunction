# T-032: admin: the state of the thicket
execute store result score #c le.sp if entity @e[type=minecraft:spider,tag=le.sp_el]
execute store result score #c2 le.sp if entity @e[type=minecraft:spider,tag=le.spawk]
execute store result score #c3 le.sp if entity @e[type=minecraft:spider,tag=le.sp_boss]
execute store result score #q le.sp run data get storage last_ember:heather q
tellraw @s [{"text":"spiders: elites ","color":"gray"},{"score":{"name":"#c","objective":"le.sp"}},{"text":" (awake "},{"score":{"name":"#c2","objective":"le.sp"}},{"text":"), mistress "},{"score":{"name":"#c3","objective":"le.sp"}},{"text":" dead "},{"score":{"name":"#boss","objective":"le.sp"}},{"text":" awake "},{"score":{"name":"#bs","objective":"le.sp"}},{"text":", cuts "},{"score":{"name":"#cuts","objective":"le.sp"}},{"text":", toivo "},{"score":{"name":"#toivo","objective":"le.sp"}},{"text":", quest "},{"score":{"name":"#q","objective":"le.sp"}}]
