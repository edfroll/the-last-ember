# as the player struck by the monster of a contract (it has the tag le.lme): the blow of its region, then the drag of its contract
execute store result storage last_ember:contracts hit.d float 1 run scoreboard players get @e[tag=le.lme,limit=1] le.cdmg
function last_ember:contract/m/strike_m with storage last_ember:contracts hit
scoreboard players operation #cid le.ct = @e[tag=le.lme,limit=1] le.cnum
function last_ember:contract/gen/hurt_p
