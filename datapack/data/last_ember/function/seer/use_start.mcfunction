execute unless score @s le.spsel matches 0..1 run scoreboard players set @s le.spsel 0
# the first tick of a use: Shift = switch the spell, else cast it (the Wrath starts charging instead)
execute if predicate last_ember:sneaking run return run function last_ember:seer/switch
function last_ember:seer/gen/staff_number
execute if score #sel le.e matches 1 run return run function last_ember:seer/cast_1
execute if score #sel le.e matches 7 run return run function last_ember:seer/wrath_start
function last_ember:seer/gen/staff_cast
