# generated: every second: pending templates and visuals (when the chunk is loaded), region doors, opening by approach
execute if score #gate_west_pass le.gate matches 1 unless score #gatev_west_pass le.gate matches 1 in minecraft:overworld if loaded -648 77 -194 run function last_ember:gate/gen/vis_west_pass_1
execute if score #gate_west_pass le.gate matches 0 unless score #gatev_west_pass le.gate matches 0 in minecraft:overworld if loaded -648 77 -194 run function last_ember:gate/gen/vis_west_pass_0
execute if score #gate_south_bridge le.gate matches 1 unless score #gatev_south_bridge le.gate matches 1 in minecraft:overworld if loaded -3 126 633 run function last_ember:gate/gen/vis_south_bridge_1
execute if score #gate_south_bridge le.gate matches 0 unless score #gatev_south_bridge le.gate matches 0 in minecraft:overworld if loaded -3 126 633 run function last_ember:gate/gen/vis_south_bridge_0
execute if score #sc_r1 le.gate matches 1 unless score #scvh_r1 le.gate matches 1 in minecraft:overworld if loaded 26 103 -25 run function last_ember:gate/gen/hub_open_r1
execute if score #sc_r1 le.gate matches 0 unless score #scvh_r1 le.gate matches 0 in minecraft:overworld if loaded 26 103 -25 run function last_ember:gate/gen/hub_close_r1
execute if score #sc_r1 le.gate matches 0 if score #schb_r1 le.gate matches 0 in minecraft:overworld if loaded 26 103 -25 run function last_ember:gate/gen/hub_close_r1
execute if score #scb_r1 le.gate matches 0 in minecraft:overworld if loaded -380 111 -196 run function last_ember:gate/gen/door_build_r1
execute if score #sc_r1 le.gate matches 1 if score #scb_r1 le.gate matches 1 unless score #scvd_r1 le.gate matches 1 in minecraft:overworld if loaded -380 111 -196 run function last_ember:gate/gen/door_open_r1
execute if score #sc_r1 le.gate matches 0 if score #scb_r1 le.gate matches 1 unless score #scvd_r1 le.gate matches 0 in minecraft:overworld if loaded -380 111 -196 run function last_ember:gate/gen/door_close_r1
execute if score #sc_r1 le.gate matches 0 if score #scb_r1 le.gate matches 1 in minecraft:overworld positioned -380 111 -196 if entity @a[distance=..24,gamemode=!spectator] run function last_ember:gate/gen/sc_open_r1
execute if score #sc_r2 le.gate matches 1 unless score #scvh_r2 le.gate matches 1 in minecraft:overworld if loaded -36 103 0 run function last_ember:gate/gen/hub_open_r2
execute if score #sc_r2 le.gate matches 0 unless score #scvh_r2 le.gate matches 0 in minecraft:overworld if loaded -36 103 0 run function last_ember:gate/gen/hub_close_r2
execute if score #sc_r2 le.gate matches 0 if score #schb_r2 le.gate matches 0 in minecraft:overworld if loaded -36 103 0 run function last_ember:gate/gen/hub_close_r2
execute if score #sc_r3 le.gate matches 1 unless score #scvh_r3 le.gate matches 1 in minecraft:overworld if loaded 0 103 -36 run function last_ember:gate/gen/hub_open_r3
execute if score #sc_r3 le.gate matches 0 unless score #scvh_r3 le.gate matches 0 in minecraft:overworld if loaded 0 103 -36 run function last_ember:gate/gen/hub_close_r3
execute if score #sc_r3 le.gate matches 0 if score #schb_r3 le.gate matches 0 in minecraft:overworld if loaded 0 103 -36 run function last_ember:gate/gen/hub_close_r3
execute if score #sc_r4 le.gate matches 1 unless score #scvh_r4 le.gate matches 1 in minecraft:overworld if loaded 13 103 35 run function last_ember:gate/gen/hub_open_r4
execute if score #sc_r4 le.gate matches 0 unless score #scvh_r4 le.gate matches 0 in minecraft:overworld if loaded 13 103 35 run function last_ember:gate/gen/hub_close_r4
execute if score #sc_r4 le.gate matches 0 if score #schb_r4 le.gate matches 0 in minecraft:overworld if loaded 13 103 35 run function last_ember:gate/gen/hub_close_r4
execute if score #sc_r5 le.gate matches 1 unless score #scvh_r5 le.gate matches 1 in minecraft:overworld if loaded -20 103 30 run function last_ember:gate/gen/hub_open_r5
execute if score #sc_r5 le.gate matches 0 unless score #scvh_r5 le.gate matches 0 in minecraft:overworld if loaded -20 103 30 run function last_ember:gate/gen/hub_close_r5
execute if score #sc_r5 le.gate matches 0 if score #schb_r5 le.gate matches 0 in minecraft:overworld if loaded -20 103 30 run function last_ember:gate/gen/hub_close_r5
execute if score #sc_r6 le.gate matches 1 unless score #scvh_r6 le.gate matches 1 in minecraft:overworld if loaded 37 103 0 run function last_ember:gate/gen/hub_open_r6
execute if score #sc_r6 le.gate matches 0 unless score #scvh_r6 le.gate matches 0 in minecraft:overworld if loaded 37 103 0 run function last_ember:gate/gen/hub_close_r6
execute if score #sc_r6 le.gate matches 0 if score #schb_r6 le.gate matches 0 in minecraft:overworld if loaded 37 103 0 run function last_ember:gate/gen/hub_close_r6
