# T-025: all 6 hearts are destroyed: the garden falls asleep, once and for good (the state is in the storage): every creaking in it
# crumbles, the eyeblossoms close (gen/blooms every 5 s keeps them closed), the faces turn outward with closed eyes when nobody looks,
# the door of the gardener's house is no longer locked
scoreboard players set #asleep le.gd 1
data modify storage last_ember:garden asleep set value 1b
function last_ember:garden/gen/crumble_all
function last_ember:garden/gen/blooms
title @a[x=150,y=-64,z=-498,dx=328,dy=384,dz=296] actionbar {"text":"Сад уснул.","color":"gray","italic":true}
execute as @a[x=150,y=-64,z=-498,dx=328,dy=384,dz=296] at @s run playsound minecraft:block.eyeblossom.close_long ambient @s ~ ~ ~ 1 0.6
execute as @a[x=150,y=-64,z=-498,dx=328,dy=384,dz=296] at @s run playsound minecraft:block.creaking_heart.idle ambient @s ~ ~ ~ 0.6 0.5
