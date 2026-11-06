# generated: the Refuge side of the shortcut r1: open (portcullis up, doors open, lanterns, banner)
setblock 21 103 -23 minecraft:air
setblock 21 104 -23 minecraft:air
setblock 21 105 -23 minecraft:air
setblock 21 106 -23 minecraft:air
setblock 21 107 -23 minecraft:air
setblock 21 108 -23 minecraft:air
setblock 21 109 -23 minecraft:air
setblock 22 103 -22 minecraft:air
setblock 22 104 -22 minecraft:air
setblock 22 105 -22 minecraft:air
setblock 22 106 -22 minecraft:air
setblock 22 107 -22 minecraft:air
setblock 22 108 -22 minecraft:air
setblock 22 109 -22 minecraft:air
setblock 23 103 -21 minecraft:air
setblock 23 104 -21 minecraft:air
setblock 23 105 -21 minecraft:air
setblock 23 106 -21 minecraft:air
setblock 23 107 -21 minecraft:air
setblock 23 108 -21 minecraft:air
setblock 23 109 -21 minecraft:air
setblock 21 103 -24 minecraft:dark_oak_door[facing=south,half=lower,hinge=left,open=true]
setblock 22 103 -23 minecraft:dark_oak_door[facing=south,half=lower,hinge=right,open=true]
setblock 23 103 -22 minecraft:dark_oak_door[facing=south,half=lower,hinge=left,open=true]
setblock 24 103 -21 minecraft:dark_oak_door[facing=south,half=lower,hinge=right,open=true]
setblock 25 108 -25 minecraft:lantern[hanging=true]
setblock 28 108 -28 minecraft:lantern[hanging=true]
setblock 21 112 -21 minecraft:green_wall_banner[facing=south]{patterns:[{pattern:"minecraft:stripe_bottom",color:"black"},{pattern:"minecraft:stripe_center",color:"lime"},{pattern:"minecraft:triangle_top",color:"green"},{pattern:"minecraft:half_horizontal_bottom",color:"black"},{pattern:"minecraft:border",color:"black"}]}
kill @e[type=minecraft:interaction,tag=le.schub,scores={le.scw=1}]
scoreboard players set #scvh_r1 le.gate 1
