# generated: the shortcut door of r1: open (chains off, lanterns, the door open)
setblock -379 115 -195 minecraft:air
setblock -379 115 -197 minecraft:air
setblock -379 114 -196 minecraft:air
setblock -379 113 -195 minecraft:air
setblock -379 113 -197 minecraft:air
setblock -382 115 -196 minecraft:lantern[hanging=true]
setblock -385 115 -196 minecraft:lantern[hanging=true]
setblock -380 111 -196 minecraft:dark_oak_door[facing=east,half=lower,hinge=left,open=true]
kill @e[type=minecraft:interaction,tag=le.scdoor,scores={le.scw=1}]
scoreboard players set #scvd_r1 le.gate 1
