# generated: every second: the hints of every trap that has a player within 24 blocks
execute in minecraft:overworld positioned -478 134 367 if entity @a[distance=..24] run function last_ember:trap/gen/hint_fens_ambush
