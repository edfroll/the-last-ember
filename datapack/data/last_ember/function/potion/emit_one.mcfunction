# as the cauldron: storage last_ember:pt it becomes an item above the cauldron
data remove storage last_ember:pt it.Slot
summon minecraft:item ~ ~1.3 ~ {Item:{id:"minecraft:stone",count:1},Tags:["le.newit"],Motion:[0.0d,0.25d,0.0d],PickupDelay:10s}
data modify entity @e[type=minecraft:item,tag=le.newit,limit=1,sort=nearest,distance=..2] Item set from storage last_ember:pt it
tag @e[type=minecraft:item,tag=le.newit,distance=..2] remove le.newit
