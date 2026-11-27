# TEST/ADMIN: the treasury r1_grotto again closed and full (its main items by the current layout; a taken staff can repeat)
execute in minecraft:overworld run setblock -373 136 213 minecraft:air replace
function last_ember:vault/gen/build_r1_grotto
scoreboard players set #o.r1_grotto le.vt 0
advancement revoke @a only last_ember:vault/open_r1_grotto
