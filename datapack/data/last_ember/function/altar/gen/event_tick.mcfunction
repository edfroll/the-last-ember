# generated: every tick, the events that run (ev >= 0)
scoreboard players set #ev le.alt -1
execute store result score #ev le.alt run data get storage last_ember:altars a.weepers.ev
execute if score #ev le.alt matches 0.. in minecraft:overworld positioned -420 111 -180 run function last_ember:altar/gen/ev_weepers
