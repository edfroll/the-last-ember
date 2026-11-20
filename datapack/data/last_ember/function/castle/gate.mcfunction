# T-028: advancement reward: a click on the locked gate of the barbican (opened by the castle task)
advancement revoke @s only last_ember:castle/gate
scoreboard players add #gates le.cas 1
title @s actionbar {"text":"Замок спит. Ворота заперты изнутри.","color":"gray","italic":true}
playsound minecraft:block.iron_door.close block @s ~ ~ ~ 0.8 0.5
playsound minecraft:block.chain.step block @s ~ ~ ~ 1 0.6
