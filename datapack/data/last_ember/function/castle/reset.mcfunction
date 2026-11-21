# T-028: admin/test: the approaches as in a new world (living lake, the ambush ready, nobody waking, no passes)
scoreboard players set #faded le.cas 0
scoreboard players set #eyes le.cas 0
scoreboard players set #amb le.cas 0
scoreboard players set #ambt le.cas 0
scoreboard players set #recog le.cas 0
tag @a remove le.cpass
tag @a remove le.cwake
tag @a remove le.cfly
scoreboard players set @a le.cg 0
scoreboard players set @a le.co 0
kill @e[type=minecraft:skeleton,tag=le.camb]
function last_ember:castle/save
