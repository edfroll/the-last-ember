# a staff for r5: one at random of those that fit; return 0 when none
scoreboard players set #n le.vt 0
execute if score #p.1 le.vt matches 0 run scoreboard players add #n le.vt 1
execute if score #p.2 le.vt matches 0 run scoreboard players add #n le.vt 1
execute if score #p.3 le.vt matches 0 run scoreboard players add #n le.vt 1
execute if score #p.4 le.vt matches 0 run scoreboard players add #n le.vt 1
execute if score #p.5 le.vt matches 0 run scoreboard players add #n le.vt 1
execute if score #n le.vt matches 0 run return 0
execute store result score #r le.vt run random value 0..9999
scoreboard players operation #r le.vt %= #n le.vt
execute if score #p.1 le.vt matches 0 run scoreboard players remove #r le.vt 1
execute if score #r le.vt matches -1 if score #p.1 le.vt matches 0 run return run function last_ember:vault/gen/stf_1_r5
execute if score #p.2 le.vt matches 0 run scoreboard players remove #r le.vt 1
execute if score #r le.vt matches -1 if score #p.2 le.vt matches 0 run return run function last_ember:vault/gen/stf_2_r5
execute if score #p.3 le.vt matches 0 run scoreboard players remove #r le.vt 1
execute if score #r le.vt matches -1 if score #p.3 le.vt matches 0 run return run function last_ember:vault/gen/stf_3_r5
execute if score #p.4 le.vt matches 0 run scoreboard players remove #r le.vt 1
execute if score #r le.vt matches -1 if score #p.4 le.vt matches 0 run return run function last_ember:vault/gen/stf_4_r5
execute if score #p.5 le.vt matches 0 run scoreboard players remove #r le.vt 1
execute if score #r le.vt matches -1 if score #p.5 le.vt matches 0 run return run function last_ember:vault/gen/stf_5_r5
return 0
