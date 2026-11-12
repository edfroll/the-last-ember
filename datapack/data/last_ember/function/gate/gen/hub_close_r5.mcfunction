# generated: the Refuge side of the shortcut r5: closed (T-008 state)
setblock -19 103 24 minecraft:iron_bars[north=false,south=true,west=true,east=false]
setblock -19 104 24 minecraft:iron_bars[north=false,south=true,west=true,east=false]
setblock -19 105 24 minecraft:iron_bars[north=false,south=true,west=true,east=false]
setblock -19 106 24 minecraft:iron_bars[north=false,south=true,west=true,east=false]
setblock -19 107 24 minecraft:iron_bars[north=false,south=true,west=true,east=false]
setblock -19 108 24 minecraft:iron_bars[north=false,south=true,west=true,east=false]
setblock -19 109 24 minecraft:iron_bars[north=false,south=true,west=true,east=false]
setblock -19 103 25 minecraft:iron_bars[north=true,south=false,west=false,east=true]
setblock -19 104 25 minecraft:iron_bars[north=true,south=false,west=false,east=true]
setblock -19 105 25 minecraft:iron_bars[north=true,south=true,west=true,east=true]
setblock -19 106 25 minecraft:iron_bars[north=true,south=true,west=true,east=true]
setblock -19 107 25 minecraft:iron_bars[north=true,south=true,west=true,east=true]
setblock -19 108 25 minecraft:iron_bars[north=true,south=true,west=true,east=true]
setblock -19 109 25 minecraft:iron_bars[north=true,south=true,west=true,east=true]
setblock -18 103 25 minecraft:iron_bars[north=false,south=true,west=true,east=false]
setblock -18 104 25 minecraft:iron_bars[north=false,south=true,west=true,east=false]
setblock -18 105 25 minecraft:iron_bars[north=false,south=true,west=true,east=false]
setblock -18 106 25 minecraft:iron_bars[north=false,south=true,west=true,east=false]
setblock -18 107 25 minecraft:iron_bars[north=false,south=true,west=true,east=false]
setblock -18 108 25 minecraft:iron_bars[north=false,south=true,west=true,east=false]
setblock -18 109 25 minecraft:iron_bars[north=false,south=true,west=true,east=false]
setblock -17 103 26 minecraft:iron_bars[north=false,south=false,west=true,east=false]
setblock -17 104 26 minecraft:iron_bars[north=false,south=false,west=true,east=false]
setblock -17 105 26 minecraft:iron_bars[north=false,south=true,west=true,east=false]
setblock -17 106 26 minecraft:iron_bars[north=false,south=true,west=true,east=false]
setblock -17 107 26 minecraft:iron_bars[north=false,south=true,west=true,east=false]
setblock -17 108 26 minecraft:iron_bars[north=false,south=true,west=true,east=false]
setblock -17 109 26 minecraft:iron_bars[north=false,south=true,west=true,east=false]
setblock -16 103 27 minecraft:iron_bars[north=false,south=true,west=false,east=true]
setblock -16 104 27 minecraft:iron_bars[north=false,south=true,west=false,east=true]
setblock -16 105 27 minecraft:iron_bars[north=false,south=true,west=true,east=true]
setblock -16 106 27 minecraft:iron_bars[north=false,south=true,west=true,east=true]
setblock -16 107 27 minecraft:iron_bars[north=false,south=true,west=true,east=true]
setblock -16 108 27 minecraft:iron_bars[north=false,south=true,west=true,east=true]
setblock -16 109 27 minecraft:iron_bars[north=false,south=true,west=true,east=true]
setblock -20 103 25 minecraft:dark_oak_door[facing=north,half=lower,hinge=right,open=false]
setblock -19 103 26 minecraft:dark_oak_door[facing=north,half=lower,hinge=left,open=false]
setblock -18 103 27 minecraft:dark_oak_door[facing=north,half=lower,hinge=right,open=false]
setblock -17 103 27 minecraft:dark_oak_door[facing=north,half=lower,hinge=left,open=false]
setblock -20 108 29 minecraft:air
setblock -22 108 32 minecraft:air
setblock -17 112 24 minecraft:air
kill @e[type=minecraft:interaction,tag=le.schub,scores={le.scw=5}]
summon minecraft:interaction -16.7 103 25.1 {Tags:["le.schub","le.scclick","le.scnew"],width:5f,height:7f,response:1b}
scoreboard players set @e[type=minecraft:interaction,tag=le.scnew] le.scw 5
tag @e[type=minecraft:interaction,tag=le.scnew] remove le.scnew
scoreboard players set #scvh_r5 le.gate 0
scoreboard players set #schb_r5 le.gate 1
