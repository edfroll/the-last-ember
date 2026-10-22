# generated: traders whose chunk is loaded are put in place once (every second)
execute if score #trader_smith_bl le.tr matches 0 in minecraft:overworld if loaded 58 101 27 run function last_ember:trader/gen/build_smith
