# generated: build the board r0 (the signs if build=1, the click boxes, the texts)
scoreboard players set #b_r0_bl le.ct 1
execute in minecraft:overworld run kill @e[type=minecraft:interaction,tag=le.cb_r0]
execute in minecraft:overworld run summon minecraft:interaction -59.50 103.05 22.80 {Tags:["le.cboard","le.cb_r0"],width:0.9f,height:0.75f,response:1b}
execute in minecraft:overworld positioned -59.50 103.05 22.80 run scoreboard players set @e[type=minecraft:interaction,tag=le.cb_r0,distance=..0.1] le.cslot 101
execute in minecraft:overworld run summon minecraft:interaction -57.50 103.05 22.80 {Tags:["le.cboard","le.cb_r0"],width:0.9f,height:0.75f,response:1b}
execute in minecraft:overworld positioned -57.50 103.05 22.80 run scoreboard players set @e[type=minecraft:interaction,tag=le.cb_r0,distance=..0.1] le.cslot 102
execute in minecraft:overworld run summon minecraft:interaction -55.50 103.05 22.80 {Tags:["le.cboard","le.cb_r0"],width:0.9f,height:0.75f,response:1b}
execute in minecraft:overworld positioned -55.50 103.05 22.80 run scoreboard players set @e[type=minecraft:interaction,tag=le.cb_r0,distance=..0.1] le.cslot 103
execute in minecraft:overworld run summon minecraft:interaction -59.50 102.05 22.80 {Tags:["le.cboard","le.cb_r0"],width:0.9f,height:0.75f,response:1b}
execute in minecraft:overworld positioned -59.50 102.05 22.80 run scoreboard players set @e[type=minecraft:interaction,tag=le.cb_r0,distance=..0.1] le.cslot 104
execute in minecraft:overworld run summon minecraft:interaction -57.50 102.05 22.80 {Tags:["le.cboard","le.cb_r0"],width:0.9f,height:0.75f,response:1b}
execute in minecraft:overworld positioned -57.50 102.05 22.80 run scoreboard players set @e[type=minecraft:interaction,tag=le.cb_r0,distance=..0.1] le.cslot 105
execute in minecraft:overworld run summon minecraft:interaction -55.50 102.05 22.80 {Tags:["le.cboard","le.cb_r0"],width:0.9f,height:0.75f,response:1b}
execute in minecraft:overworld positioned -55.50 102.05 22.80 run scoreboard players set @e[type=minecraft:interaction,tag=le.cb_r0,distance=..0.1] le.cslot 106
function last_ember:contract/gen/board_r0
