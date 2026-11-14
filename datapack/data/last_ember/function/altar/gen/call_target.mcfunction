# generated: as the carrier: #tx le.alt #tz le.alt = the nearest source of a key of the current chapter that nobody has found yet; #found = 1 when there is one
scoreboard players set #found le.alt 0
scoreboard players set #best le.alt 2147483647
execute store result score #px le.alt run data get entity @s Pos[0]
execute store result score #pz le.alt run data get entity @s Pos[2]
execute if data storage last_ember:keys k.signet_king{got:0b} if score #cur le.alt matches 1 if dimension minecraft:overworld run function last_ember:altar/gen/call_signet_king
execute if data storage last_ember:keys k.tear_creaker{got:0b} if score #cur le.alt matches 1 if dimension minecraft:overworld run function last_ember:altar/gen/call_tear_creaker
execute if data storage last_ember:keys k.crown_witches{got:0b} if score #cur le.alt matches 1 if dimension minecraft:overworld run function last_ember:altar/gen/call_crown_witches
execute if data storage last_ember:keys k.thread_labyrinth{got:0b} if score #cur le.alt matches 1 if dimension minecraft:overworld run function last_ember:altar/gen/call_thread_labyrinth
# nothing to look for: the altar of the chapter
execute if score #found le.alt matches 0 if score #cur le.alt matches 1 run function last_ember:altar/gen/take_altar_weepers
