# T-028: every 5 ticks: the carriers of the seal, the players at the castle (trigger, rock, the pass), the eyes, the ambush; every second
# castle/second (the faded lake, the gate's click box, the state in storage)
schedule function last_ember:castle/loop 5t replace
execute store result score #gt le.cas run time query gametime
scoreboard players add #t le.cas 5
tag @a remove le.sealh
execute as @a[gamemode=!spectator,gamemode=!creative] if items entity @s container.* *[minecraft:custom_data~{le_citem:"seal"}] run tag @s add le.sealh
execute as @a[gamemode=!spectator,gamemode=!creative,tag=!le.sealh] if items entity @s weapon.offhand *[minecraft:custom_data~{le_citem:"seal"}] run tag @s add le.sealh
# the pass is lost after 5 s outside the rock and the trigger (also far from the castle, offline time does not count)
execute in minecraft:overworld as @a[tag=le.cpass] unless entity @s[x=330,y=40,z=-130,dx=250,dy=280,dz=260] run scoreboard players add @s le.co 1
execute as @a[tag=le.cpass,scores={le.co=20..}] run tag @s remove le.cpass
execute if score #faded le.cas matches 0 in minecraft:overworld as @a[x=330,y=40,z=-130,dx=250,dy=280,dz=260,gamemode=!spectator,gamemode=!creative,tag=!le.cwake,tag=!le.cfly] at @s run function last_ember:castle/player
execute if entity @a[tag=le.cwake] run schedule function last_ember:castle/tick 1t replace
execute if entity @a[tag=le.cfly] run schedule function last_ember:castle/tick 1t replace
# the eyes: asleep again when nobody is waking or flying and the time is up; empty in the faded lake
execute if score #eyes le.cas matches 1..2 if score #gt le.cas >= #eyet le.cas unless entity @a[tag=le.cwake] unless entity @a[tag=le.cfly] run scoreboard players set #eyes le.cas 0
execute if score #faded le.cas matches 1 run scoreboard players set #eyes le.cas 3
execute if score #faded le.cas matches 0 if score #eyes le.cas matches 3 run scoreboard players set #eyes le.cas 0
execute unless score #eyesv le.cas = #eyes le.cas in minecraft:overworld run function last_ember:castle/gen/eyes_sync
execute if score #amb le.cas matches 0 in minecraft:overworld run function last_ember:castle/ambush_try
scoreboard players operation #t20 le.cas = #t le.cas
scoreboard players operation #t20 le.cas %= #20 le.cas
execute if score #t20 le.cas matches 0 in minecraft:overworld run function last_ember:castle/second
