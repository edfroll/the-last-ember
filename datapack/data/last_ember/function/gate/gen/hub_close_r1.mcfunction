# generated: the Refuge side of the shortcut r1: closed (T-008 state)
setblock 21 103 -23 minecraft:iron_bars[north=false,south=false,west=false,east=false]
setblock 21 104 -23 minecraft:iron_bars[north=false,south=false,west=false,east=false]
setblock 21 105 -23 minecraft:iron_bars[north=true,south=false,west=false,east=true]
setblock 21 106 -23 minecraft:iron_bars[north=true,south=false,west=false,east=true]
setblock 21 107 -23 minecraft:iron_bars[north=true,south=false,west=false,east=true]
setblock 21 108 -23 minecraft:iron_bars[north=true,south=false,west=false,east=true]
setblock 21 109 -23 minecraft:iron_bars[north=true,south=false,west=false,east=true]
setblock 22 103 -22 minecraft:iron_bars[north=false,south=false,west=false,east=false]
setblock 22 104 -22 minecraft:iron_bars[north=false,south=false,west=false,east=false]
setblock 22 105 -22 minecraft:iron_bars[north=true,south=false,west=false,east=true]
setblock 22 106 -22 minecraft:iron_bars[north=true,south=false,west=false,east=true]
setblock 22 107 -22 minecraft:iron_bars[north=true,south=false,west=false,east=true]
setblock 22 108 -22 minecraft:iron_bars[north=true,south=false,west=false,east=true]
setblock 22 109 -22 minecraft:iron_bars[north=true,south=false,west=false,east=true]
setblock 23 103 -21 minecraft:iron_bars[north=false,south=false,west=false,east=false]
setblock 23 104 -21 minecraft:iron_bars[north=false,south=false,west=false,east=false]
setblock 23 105 -21 minecraft:iron_bars[north=true,south=false,west=false,east=true]
setblock 23 106 -21 minecraft:iron_bars[north=true,south=false,west=false,east=true]
setblock 23 107 -21 minecraft:iron_bars[north=true,south=false,west=false,east=true]
setblock 23 108 -21 minecraft:iron_bars[north=true,south=false,west=false,east=true]
setblock 23 109 -21 minecraft:iron_bars[north=true,south=false,west=false,east=true]
setblock 21 103 -24 minecraft:dark_oak_door[facing=south,half=lower,hinge=left,open=false]
setblock 22 103 -23 minecraft:dark_oak_door[facing=south,half=lower,hinge=right,open=false]
setblock 23 103 -22 minecraft:dark_oak_door[facing=south,half=lower,hinge=left,open=false]
setblock 24 103 -21 minecraft:dark_oak_door[facing=south,half=lower,hinge=right,open=false]
setblock 25 108 -25 minecraft:air
setblock 28 108 -28 minecraft:air
setblock 21 112 -21 minecraft:air
kill @e[type=minecraft:interaction,tag=le.schub,scores={le.scw=1}]
summon minecraft:interaction 21.7 103 -20.7 {Tags:["le.schub","le.scclick","le.scnew"],width:5f,height:7f,response:1b}
scoreboard players set @e[type=minecraft:interaction,tag=le.scnew] le.scw 1
tag @e[type=minecraft:interaction,tag=le.scnew] remove le.scnew
scoreboard players set #scvh_r1 le.gate 0
scoreboard players set #schb_r1 le.gate 1
