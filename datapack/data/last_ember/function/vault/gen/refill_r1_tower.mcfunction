# TEST/ADMIN: the treasury r1_tower again closed and full (its main items by the current layout; a taken staff can repeat)
execute in minecraft:overworld run setblock 477 190 43 minecraft:air replace
function last_ember:vault/gen/build_r1_tower
scoreboard players set #o.r1_tower le.vt 0
advancement revoke @a only last_ember:vault/open_r1_tower
