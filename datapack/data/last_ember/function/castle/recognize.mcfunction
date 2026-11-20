# T-028: a protected player (within 10 of the carrier of the seal) in the trigger: let through; the first time in 60 s the eyes glow dimly
# for 2 s, a low hum, «Колоссы узнают печать.»
tag @s add le.cpass
scoreboard players set @s le.co 0
execute if score #recog le.cas > #gt le.cas run return 0
scoreboard players operation #recog le.cas = #gt le.cas
scoreboard players add #recog le.cas 1200
execute unless score #eyes le.cas matches 1 run scoreboard players operation #eyet le.cas = #gt le.cas
execute unless score #eyes le.cas matches 1 run scoreboard players add #eyet le.cas 40
execute unless score #eyes le.cas matches 1 run scoreboard players set #eyes le.cas 2
execute unless score #eyesv le.cas = #eyes le.cas run function last_ember:castle/gen/eyes_sync
playsound minecraft:block.beacon.ambient ambient @a[distance=..48] ~ ~ ~ 2 0.5
playsound minecraft:block.conduit.ambient ambient @a[distance=..48] ~ ~ ~ 2 0.5
title @a[distance=..32] actionbar {"text":"Колоссы узнают печать.","color":"gray","italic":true}
