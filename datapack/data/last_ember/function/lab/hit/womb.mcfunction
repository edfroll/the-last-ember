advancement revoke @s only last_ember:lab/hit_womb
function last_ember:lab/s/womb_hit
function last_ember:wound/murk
# T-020: the womb of a contract may drag its prey
execute as @e[tag=le.contract,tag=le.lab_womb,distance=..6,sort=nearest,limit=1] run scoreboard players operation #cid le.ct = @s le.cnum
execute if entity @e[tag=le.contract,tag=le.lab_womb,distance=..6] run function last_ember:contract/gen/hurt_p
