# generated: the shortcut door of r1: locked (TEST)
setblock -379 115 -195 minecraft:iron_chain[axis=y]
setblock -379 115 -197 minecraft:iron_chain[axis=y]
setblock -379 114 -196 minecraft:iron_chain[axis=y]
setblock -379 113 -195 minecraft:iron_chain[axis=y]
setblock -379 113 -197 minecraft:iron_chain[axis=y]
setblock -382 115 -196 minecraft:air
setblock -385 115 -196 minecraft:air
setblock -380 111 -196 minecraft:dark_oak_door[facing=east,half=lower,hinge=left,open=false]
kill @e[type=minecraft:interaction,tag=le.scdoor,scores={le.scw=1}]
summon minecraft:interaction -378.5 111 -195.5 {Tags:["le.scdoor","le.scclick","le.scnew"],width:1.2f,height:2.2f,response:1b}
scoreboard players set @e[type=minecraft:interaction,tag=le.scnew] le.scw 1
tag @e[type=minecraft:interaction,tag=le.scnew] remove le.scnew
scoreboard players set #scvd_r1 le.gate 0
