# generated: the Refuge side of the shortcut r3: closed (T-008 state)
setblock -2 103 -31 minecraft:iron_bars[north=false,south=false,west=true,east=true]
setblock -2 104 -31 minecraft:iron_bars[north=false,south=false,west=true,east=true]
setblock -2 105 -31 minecraft:iron_bars[north=true,south=false,west=true,east=true]
setblock -2 106 -31 minecraft:iron_bars[north=true,south=false,west=true,east=true]
setblock -2 107 -31 minecraft:iron_bars[north=true,south=false,west=true,east=true]
setblock -2 108 -31 minecraft:iron_bars[north=true,south=false,west=true,east=true]
setblock -2 109 -31 minecraft:iron_bars[north=true,south=false,west=true,east=true]
setblock -1 103 -31 minecraft:iron_bars[north=false,south=false,west=true,east=true]
setblock -1 104 -31 minecraft:iron_bars[north=false,south=false,west=true,east=true]
setblock -1 105 -31 minecraft:iron_bars[north=true,south=false,west=true,east=true]
setblock -1 106 -31 minecraft:iron_bars[north=true,south=false,west=true,east=true]
setblock -1 107 -31 minecraft:iron_bars[north=true,south=false,west=true,east=true]
setblock -1 108 -31 minecraft:iron_bars[north=true,south=false,west=true,east=true]
setblock -1 109 -31 minecraft:iron_bars[north=true,south=false,west=true,east=true]
setblock 0 103 -31 minecraft:iron_bars[north=true,south=false,west=true,east=true]
setblock 0 104 -31 minecraft:iron_bars[north=true,south=false,west=true,east=true]
setblock 0 105 -31 minecraft:iron_bars[north=true,south=false,west=true,east=true]
setblock 0 106 -31 minecraft:iron_bars[north=true,south=false,west=true,east=true]
setblock 0 107 -31 minecraft:iron_bars[north=true,south=false,west=true,east=true]
setblock 0 108 -31 minecraft:iron_bars[north=true,south=false,west=true,east=true]
setblock 0 109 -31 minecraft:iron_bars[north=true,south=false,west=true,east=true]
setblock 1 103 -31 minecraft:iron_bars[north=false,south=false,west=true,east=true]
setblock 1 104 -31 minecraft:iron_bars[north=false,south=false,west=true,east=true]
setblock 1 105 -31 minecraft:iron_bars[north=true,south=false,west=true,east=true]
setblock 1 106 -31 minecraft:iron_bars[north=true,south=false,west=true,east=true]
setblock 1 107 -31 minecraft:iron_bars[north=true,south=false,west=true,east=true]
setblock 1 108 -31 minecraft:iron_bars[north=true,south=false,west=true,east=true]
setblock 1 109 -31 minecraft:iron_bars[north=true,south=false,west=true,east=true]
setblock 2 103 -31 minecraft:iron_bars[north=false,south=false,west=true,east=true]
setblock 2 104 -31 minecraft:iron_bars[north=false,south=false,west=true,east=true]
setblock 2 105 -31 minecraft:iron_bars[north=true,south=false,west=true,east=true]
setblock 2 106 -31 minecraft:iron_bars[north=true,south=false,west=true,east=true]
setblock 2 107 -31 minecraft:iron_bars[north=true,south=false,west=true,east=true]
setblock 2 108 -31 minecraft:iron_bars[north=true,south=false,west=true,east=true]
setblock 2 109 -31 minecraft:iron_bars[north=true,south=false,west=true,east=true]
setblock -2 103 -32 minecraft:dark_oak_door[facing=south,half=lower,hinge=left,open=false]
setblock -1 103 -32 minecraft:dark_oak_door[facing=south,half=lower,hinge=right,open=false]
setblock 1 103 -32 minecraft:dark_oak_door[facing=south,half=lower,hinge=left,open=false]
setblock 2 103 -32 minecraft:dark_oak_door[facing=south,half=lower,hinge=right,open=false]
setblock 0 108 -35 minecraft:air
setblock 0 108 -39 minecraft:air
setblock 0 112 -29 minecraft:air
kill @e[type=minecraft:interaction,tag=le.schub,scores={le.scw=3}]
summon minecraft:interaction 0.5 103 -29.5 {Tags:["le.schub","le.scclick","le.scnew"],width:5f,height:7f,response:1b}
scoreboard players set @e[type=minecraft:interaction,tag=le.scnew] le.scw 3
tag @e[type=minecraft:interaction,tag=le.scnew] remove le.scnew
scoreboard players set #scvh_r3 le.gate 0
scoreboard players set #schb_r3 le.gate 1
