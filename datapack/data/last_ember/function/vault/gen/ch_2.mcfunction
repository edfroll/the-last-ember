# the second main slot: one at random of those that fit; return 0 when none
scoreboard players set #n le.vt 0
execute unless score #o.r1_ogre le.vt matches 1 if score #m2.r1_ogre le.vt matches 0 run scoreboard players add #n le.vt 1
execute if score #n le.vt matches 0 run return 0
execute store result score #r le.vt run random value 0..9999
scoreboard players operation #r le.vt %= #n le.vt
execute unless score #o.r1_ogre le.vt matches 1 if score #m2.r1_ogre le.vt matches 0 run scoreboard players remove #r le.vt 1
execute if score #r le.vt matches -1 unless score #o.r1_ogre le.vt matches 1 if score #m2.r1_ogre le.vt matches 0 run return run scoreboard players operation #m2.r1_ogre le.vt = #k le.vt
return 0
