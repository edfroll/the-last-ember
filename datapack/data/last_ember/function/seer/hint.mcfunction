# as a seer: the name of the selected spell over the hotbar, with the cooldown while it runs
function last_ember:seer/gen/staff_number
function last_ember:seer/gen/spell_name
function last_ember:seer/gen/cd_remaining
execute store result storage last_ember:seer h.secs int 1 run scoreboard players get #r le.e
data modify storage last_ember:seer h.tail set value ""
execute if score #r le.e matches 1.. run function last_ember:seer/hint_tail with storage last_ember:seer h
function last_ember:seer/hint_m with storage last_ember:seer h
