# T-025: as the player who takes the Tear of the Creaker: the key goes to the inventory through the key system of T-013 (the current
# generation; the Call of the Ember no longer leads here: got = 1b); the pedestal is empty for good. Independent of the hearts.
scoreboard players set #key le.gd 2
data modify storage last_ember:garden key set value 2b
kill @e[type=minecraft:item_display,tag=le.gdkey_disp]
kill @e[type=minecraft:interaction,tag=le.gdkey]
function last_ember:altar/gen/item_tear_creaker with storage last_ember:keys k.tear_creaker
data modify storage last_ember:keys k.tear_creaker.got set value 1b
function last_ember:garden/gen/key_fx
