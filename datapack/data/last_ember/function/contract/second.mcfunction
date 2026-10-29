scoreboard players set #sec le.ct 0
execute store result score #online le.ct if entity @a[gamemode=!spectator,gamemode=!creative]
function last_ember:contract/gen/bp
function last_ember:contract/gen/sec
# the blood trail of a dragged player: seen by the others who crouch (rangers standing too)
execute as @e[type=minecraft:marker,tag=le.ctrail] at @s run particle minecraft:dust{color:[0.6,0.02,0.02],scale:1.2} ~ ~0.1 ~ 0.3 0.05 0.3 0 5 force @a[distance=..20,tag=!le.dragged,predicate=last_ember:sneaking]
execute as @e[type=minecraft:marker,tag=le.ctrail] at @s run particle minecraft:dust{color:[0.6,0.02,0.02],scale:1.2} ~ ~0.1 ~ 0.3 0.05 0.3 0 5 force @a[distance=..20,tag=!le.dragged,tag=le.class.ranger]
