# TEST/ADMIN: the treasury r1_ogre again closed and full (its main items by the current layout; a taken staff can repeat)
execute in minecraft:overworld run setblock 222 170 149 minecraft:air replace
function last_ember:vault/gen/build_r1_ogre
scoreboard players set #o.r1_ogre le.vt 0
advancement revoke @a only last_ember:vault/open_r1_ogre
