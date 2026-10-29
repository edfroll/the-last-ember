# the start staff: a random one of five (no Wrath of the Dead Sky) of those nobody has taken yet (T-019: vault/gen/staff_pick takes it out of its treasury)
function last_ember:vault/gen/staff_pick
execute if score #rnd le.e matches 1 run function last_ember:seer/gen/give_blink
execute if score #rnd le.e matches 2 run function last_ember:seer/gen/give_frost
execute if score #rnd le.e matches 3 run function last_ember:seer/gen/give_flame
execute if score #rnd le.e matches 4 run function last_ember:seer/gen/give_lift
execute if score #rnd le.e matches 5 run function last_ember:seer/gen/give_banish
