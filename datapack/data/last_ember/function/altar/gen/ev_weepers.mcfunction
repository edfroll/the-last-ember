# generated: one tick of the event of weepers (at the altar); #ev = the tick number
execute store result score #ev le.alt run data get storage last_ember:altars a.weepers.ev
execute store result storage last_ember:altars a.weepers.ev int 1 run scoreboard players add #ev le.alt 1
execute if score #ev le.alt matches 1 run playsound minecraft:block.beacon.activate block @a[distance=..40] ~ ~ ~ 2 0.5
execute if score #ev le.alt matches 1 run title @a[distance=..40] actionbar {"text":"Гул под землёй…","color":"gray"}
execute if score #ev le.alt matches 20 run playsound minecraft:ambient.cave block @a[distance=..40] ~ ~ ~ 2 0.5
execute if score #ev le.alt matches 40 run playsound minecraft:block.beacon.ambient block @a[distance=..40] ~ ~ ~ 2 0.6
execute if score #ev le.alt matches 150 run playsound minecraft:entity.lightning_bolt.thunder weather @a[distance=..80] ~ ~ ~ 5 0.7
function last_ember:weepers/ev
scoreboard players operation #m le.alt = #ev le.alt
scoreboard players operation #m le.alt %= #5 le.alt
execute if score #m le.alt matches 0 positioned -413.5 112.4 -185.5 facing entity @a[tag=le.carrier,limit=1,sort=nearest] eyes run function last_ember:altar/beam
execute if score #m le.alt matches 0 run particle minecraft:enchant -413.5 112.4 -185.5 0.3 0.3 0.3 0.5 4
execute if score #m le.alt matches 0 positioned -410.5 112.4 -179.5 facing entity @a[tag=le.carrier,limit=1,sort=nearest] eyes run function last_ember:altar/beam
execute if score #m le.alt matches 0 run particle minecraft:enchant -410.5 112.4 -179.5 0.3 0.3 0.3 0.5 4
execute if score #m le.alt matches 0 positioned -413.5 112.4 -173.5 facing entity @a[tag=le.carrier,limit=1,sort=nearest] eyes run function last_ember:altar/beam
execute if score #m le.alt matches 0 run particle minecraft:enchant -413.5 112.4 -173.5 0.3 0.3 0.3 0.5 4
execute if score #m le.alt matches 0 positioned -419.5 112.4 -170.5 facing entity @a[tag=le.carrier,limit=1,sort=nearest] eyes run function last_ember:altar/beam
execute if score #m le.alt matches 0 run particle minecraft:enchant -419.5 112.4 -170.5 0.3 0.3 0.3 0.5 4
execute if score #ev le.alt matches 260.. run function last_ember:altar/gen/done_weepers
