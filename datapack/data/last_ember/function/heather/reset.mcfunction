# T-031: admin: the village as in a new world: the quest 0, the acquaintances again, every dead villager on his point now, the ringer,
# the sails, the scarecrows
data modify storage last_ember:heather q set value 0
scoreboard players add #met le.hv 1
scoreboard players set #frz le.hv 0
kill @e[type=minecraft:zombie_villager,tag=le.hz]
function last_ember:heather/gen/dawn_all
function last_ember:heather/gen/ringer_put
function last_ember:heather/gen/sails_put
kill @e[type=minecraft:armor_stand,tag=le.hscare]
tellraw @s {"text":"heather: reset","color":"gray"}
