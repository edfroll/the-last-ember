# generated: registered but not yet built bonfires are built once their chunk is loaded (checked every second)
execute if data storage last_ember:bonfires by.b1{built:0b} in minecraft:overworld if loaded 0 105 0 positioned 0 105 0 run function last_ember:bonfire/build_now {i:1}
