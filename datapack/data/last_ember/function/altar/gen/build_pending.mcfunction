# generated: registered altars whose chunk is loaded get their interactions and labels (every second)
execute if data storage last_ember:altars a.weepers{built:0b} in minecraft:overworld if loaded -420 111 -180 run function last_ember:altar/gen/build_weepers
