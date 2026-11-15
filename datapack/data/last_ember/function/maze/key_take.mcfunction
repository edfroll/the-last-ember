# T-024: as the player who takes the Thread of the Labyrinth: the key goes to the inventory through the key system of T-013 (the current
# generation; the Call of the Ember no longer leads here: got = 1b), the pedestal is empty for good, the secret exit opens, the 4 guards
# wake (1 s of dust and scraping, then they live)
scoreboard players set #key le.mz 2
execute store result score #ktk le.mz run time query gametime
data modify storage last_ember:maze key set value 2
kill @e[type=minecraft:item_display,tag=le.mzkey_disp]
kill @e[type=minecraft:interaction,tag=le.mzkey]
function last_ember:altar/gen/item_thread_labyrinth with storage last_ember:keys k.thread_labyrinth
data modify storage last_ember:keys k.thread_labyrinth.got set value 1b
playsound minecraft:block.vault.open_shutter block @a[distance=..24] -150 113 -430 1 0.6
particle minecraft:enchant -150 114 -430 0.4 0.4 0.4 0.6 60 force
scoreboard players set #exit le.mz 1
data modify storage last_ember:maze exit set value 1
execute in minecraft:overworld if loaded -152 111 -491 if loaded -149 111 -441 run function last_ember:maze/gen/sync_exit
execute in minecraft:overworld run playsound minecraft:block.poplar_leaves.ambient block @a -150 115 -466 1.5 0.5
function last_ember:maze/gen/wake_all
