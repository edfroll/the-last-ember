# generated: traps whose chunk is loaded are built once (every second)
execute if score #fens_ambush_bl le.tr matches 0 in minecraft:overworld if loaded -478 134 367 run function last_ember:trap/gen/build_fens_ambush
