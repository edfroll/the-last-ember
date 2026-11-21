# T-028: every 5 ticks while the ambush is ready: the first player on the rest platform -> out of each niche 1 skeleton + 1 for every
# other player within 16, at most 3 a niche
scoreboard players set #onrest le.cas 0
execute as @a[x=420,y=130,z=-42,dx=16,dy=20,dz=16,gamemode=!spectator,gamemode=!creative] if function last_ember:castle/gen/on_rest run scoreboard players set #onrest le.cas 1
execute if score #onrest le.cas matches 0 run return 0
function last_ember:castle/gen/ambush_near
function last_ember:castle/gen/ambush_one
execute if score #n16 le.cas matches 2.. run function last_ember:castle/gen/ambush_one
execute if score #n16 le.cas matches 3.. run function last_ember:castle/gen/ambush_one
scoreboard players set #amb le.cas 1
scoreboard players set #ambt le.cas 0
function last_ember:castle/save
