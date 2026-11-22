# T-030: ADMIN: the acquaintance again for everybody (also the players not online: their generation no longer matches), the Advisor
# back to the day point (now when its chunk is loaded, else by the loop), unpinned
scoreboard players add #met le.grv 1
tag @a remove le.amet
scoreboard players set #pin le.grv 0
scoreboard players set #cur le.grv -1
scoreboard players add #agen le.grv 1
execute as @e[tag=le.advent] run kill @s
function last_ember:grove/gen/put_day
