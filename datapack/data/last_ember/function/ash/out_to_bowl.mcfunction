# 3 ticks after a hand-out: what the player could not pick up goes to the urn's bowl (if handed out by an urn), else stays where it is
execute if data storage last_ember:dt bowl.x run function last_ember:ash/out_to_bowl_m with storage last_ember:dt bowl
tag @e[type=minecraft:item,tag=le.out] remove le.out
data remove storage last_ember:dt bowl
