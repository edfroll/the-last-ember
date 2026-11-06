# generated: the Refuge side of the shortcut r4: closed (T-008 state)
setblock 9 103 30 minecraft:iron_bars[north=false,south=false,west=true,east=false]
setblock 9 104 30 minecraft:iron_bars[north=false,south=false,west=true,east=false]
setblock 9 105 30 minecraft:iron_bars[north=false,south=true,west=true,east=true]
setblock 9 106 30 minecraft:iron_bars[north=false,south=true,west=true,east=true]
setblock 9 107 30 minecraft:iron_bars[north=false,south=true,west=true,east=true]
setblock 9 108 30 minecraft:iron_bars[north=false,south=true,west=true,east=true]
setblock 9 109 30 minecraft:iron_bars[north=false,south=true,west=true,east=true]
setblock 10 103 29 minecraft:iron_bars[north=false,south=false,west=false,east=true]
setblock 10 104 29 minecraft:iron_bars[north=false,south=false,west=false,east=true]
setblock 10 105 29 minecraft:iron_bars[north=false,south=true,west=false,east=true]
setblock 10 106 29 minecraft:iron_bars[north=false,south=true,west=false,east=true]
setblock 10 107 29 minecraft:iron_bars[north=false,south=true,west=false,east=true]
setblock 10 108 29 minecraft:iron_bars[north=false,south=true,west=false,east=true]
setblock 10 109 29 minecraft:iron_bars[north=false,south=true,west=false,east=true]
setblock 11 103 29 minecraft:iron_bars[north=false,south=true,west=true,east=true]
setblock 11 104 29 minecraft:iron_bars[north=false,south=true,west=true,east=true]
setblock 11 105 29 minecraft:iron_bars[north=false,south=true,west=true,east=true]
setblock 11 106 29 minecraft:iron_bars[north=false,south=true,west=true,east=true]
setblock 11 107 29 minecraft:iron_bars[north=false,south=true,west=true,east=true]
setblock 11 108 29 minecraft:iron_bars[north=false,south=true,west=true,east=true]
setblock 11 109 29 minecraft:iron_bars[north=false,south=true,west=true,east=true]
setblock 12 103 29 minecraft:iron_bars[north=false,south=false,west=true,east=false]
setblock 12 104 29 minecraft:iron_bars[north=false,south=false,west=true,east=false]
setblock 12 105 29 minecraft:iron_bars[north=false,south=true,west=true,east=true]
setblock 12 106 29 minecraft:iron_bars[north=false,south=true,west=true,east=true]
setblock 12 107 29 minecraft:iron_bars[north=false,south=true,west=true,east=true]
setblock 12 108 29 minecraft:iron_bars[north=false,south=true,west=true,east=true]
setblock 12 109 29 minecraft:iron_bars[north=false,south=true,west=true,east=true]
setblock 9 103 31 minecraft:dark_oak_door[facing=north,half=lower,hinge=right,open=false]
setblock 10 103 30 minecraft:dark_oak_door[facing=north,half=lower,hinge=left,open=false]
setblock 12 103 30 minecraft:dark_oak_door[facing=north,half=lower,hinge=right,open=false]
setblock 13 103 29 minecraft:dark_oak_door[facing=north,half=lower,hinge=left,open=false]
setblock 12 108 33 minecraft:air
setblock 13 108 37 minecraft:air
setblock 10 112 27 minecraft:air
kill @e[type=minecraft:interaction,tag=le.schub,scores={le.scw=4}]
summon minecraft:interaction 10.8 103 28.7 {Tags:["le.schub","le.scclick","le.scnew"],width:5f,height:7f,response:1b}
scoreboard players set @e[type=minecraft:interaction,tag=le.scnew] le.scw 4
tag @e[type=minecraft:interaction,tag=le.scnew] remove le.scnew
scoreboard players set #scvh_r4 le.gate 0
scoreboard players set #schb_r4 le.gate 1
