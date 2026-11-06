# generated: the Refuge side of the shortcut r6: closed (T-008 state)
setblock 31 103 -2 minecraft:iron_bars[north=true,south=true,west=false,east=false]
setblock 31 104 -2 minecraft:iron_bars[north=true,south=true,west=false,east=false]
setblock 31 105 -2 minecraft:iron_bars[north=true,south=true,west=false,east=true]
setblock 31 106 -2 minecraft:iron_bars[north=true,south=true,west=false,east=true]
setblock 31 107 -2 minecraft:iron_bars[north=true,south=true,west=false,east=true]
setblock 31 108 -2 minecraft:iron_bars[north=true,south=true,west=false,east=true]
setblock 31 109 -2 minecraft:iron_bars[north=true,south=true,west=false,east=true]
setblock 31 103 -1 minecraft:iron_bars[north=true,south=true,west=false,east=false]
setblock 31 104 -1 minecraft:iron_bars[north=true,south=true,west=false,east=false]
setblock 31 105 -1 minecraft:iron_bars[north=true,south=true,west=false,east=true]
setblock 31 106 -1 minecraft:iron_bars[north=true,south=true,west=false,east=true]
setblock 31 107 -1 minecraft:iron_bars[north=true,south=true,west=false,east=true]
setblock 31 108 -1 minecraft:iron_bars[north=true,south=true,west=false,east=true]
setblock 31 109 -1 minecraft:iron_bars[north=true,south=true,west=false,east=true]
setblock 31 103 0 minecraft:iron_bars[north=true,south=true,west=false,east=true]
setblock 31 104 0 minecraft:iron_bars[north=true,south=true,west=false,east=true]
setblock 31 105 0 minecraft:iron_bars[north=true,south=true,west=false,east=true]
setblock 31 106 0 minecraft:iron_bars[north=true,south=true,west=false,east=true]
setblock 31 107 0 minecraft:iron_bars[north=true,south=true,west=false,east=true]
setblock 31 108 0 minecraft:iron_bars[north=true,south=true,west=false,east=true]
setblock 31 109 0 minecraft:iron_bars[north=true,south=true,west=false,east=true]
setblock 31 103 1 minecraft:iron_bars[north=true,south=true,west=false,east=false]
setblock 31 104 1 minecraft:iron_bars[north=true,south=true,west=false,east=false]
setblock 31 105 1 minecraft:iron_bars[north=true,south=true,west=false,east=true]
setblock 31 106 1 minecraft:iron_bars[north=true,south=true,west=false,east=true]
setblock 31 107 1 minecraft:iron_bars[north=true,south=true,west=false,east=true]
setblock 31 108 1 minecraft:iron_bars[north=true,south=true,west=false,east=true]
setblock 31 109 1 minecraft:iron_bars[north=true,south=true,west=false,east=true]
setblock 31 103 2 minecraft:iron_bars[north=true,south=true,west=false,east=false]
setblock 31 104 2 minecraft:iron_bars[north=true,south=true,west=false,east=false]
setblock 31 105 2 minecraft:iron_bars[north=true,south=true,west=false,east=true]
setblock 31 106 2 minecraft:iron_bars[north=true,south=true,west=false,east=true]
setblock 31 107 2 minecraft:iron_bars[north=true,south=true,west=false,east=true]
setblock 31 108 2 minecraft:iron_bars[north=true,south=true,west=false,east=true]
setblock 31 109 2 minecraft:iron_bars[north=true,south=true,west=false,east=true]
setblock 32 103 -2 minecraft:dark_oak_door[facing=west,half=lower,hinge=left,open=false]
setblock 32 103 -1 minecraft:dark_oak_door[facing=west,half=lower,hinge=right,open=false]
setblock 32 103 1 minecraft:dark_oak_door[facing=west,half=lower,hinge=left,open=false]
setblock 32 103 2 minecraft:dark_oak_door[facing=west,half=lower,hinge=right,open=false]
setblock 35 108 0 minecraft:air
setblock 39 108 0 minecraft:air
setblock 29 112 0 minecraft:air
kill @e[type=minecraft:interaction,tag=le.schub,scores={le.scw=6}]
summon minecraft:interaction 30.5 103 0.5 {Tags:["le.schub","le.scclick","le.scnew"],width:5f,height:7f,response:1b}
scoreboard players set @e[type=minecraft:interaction,tag=le.scnew] le.scw 6
tag @e[type=minecraft:interaction,tag=le.scnew] remove le.scnew
scoreboard players set #scvh_r6 le.gate 0
scoreboard players set #schb_r6 le.gate 1
