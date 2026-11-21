# T-028: one tick of the warning (as/at the waking player): out of the trigger and the rock, under the seal in the trigger, the pass, a
# spectator / creative -> no strike; the palms charge every 4 ticks; at 0 the strike
scoreboard players remove @s le.cw 1
scoreboard players operation #m le.cas = @s le.cw
scoreboard players operation #m le.cas %= #4 le.cas
execute if score #m le.cas matches 0 run function last_ember:castle/gen/palm_n
execute if score #m le.cas matches 0 run function last_ember:castle/gen/palm_s
execute unless entity @s[gamemode=!spectator,gamemode=!creative] run return run function last_ember:castle/calm
execute if entity @s[tag=le.cpass] run return run function last_ember:castle/calm
scoreboard players set #in le.cas 0
execute if function last_ember:castle/gen/in_trigger run scoreboard players set #in le.cas 1
execute if score #in le.cas matches 0 if function last_ember:castle/gen/in_rock run scoreboard players set #in le.cas 2
execute if score #in le.cas matches 0 run return run function last_ember:castle/calm
execute if score #in le.cas matches 1 if entity @a[tag=le.sealh,distance=..10] run return run function last_ember:castle/calm
execute if score @s le.cw matches ..0 run function last_ember:castle/strike
