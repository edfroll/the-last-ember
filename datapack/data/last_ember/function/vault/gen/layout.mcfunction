# the layout of the main items over the treasuries (at the first start, after a change of the treasury list, vault/relayout); opened treasuries keep theirs
# 1. not opened treasuries: empty
execute unless score #o.r1_ogre le.vt matches 1 run scoreboard players set #m.r1_ogre le.vt 0
execute unless score #o.r1_ogre le.vt matches 1 run scoreboard players set #m2.r1_ogre le.vt 0
execute unless score #o.r1_ogre le.vt matches 1 run scoreboard players set #a.r1_ogre le.vt 0
execute unless score #o.r1_ogre le.vt matches 1 run scoreboard players set #e.r1_ogre le.vt 0
execute unless score #o.r1_grotto le.vt matches 1 run scoreboard players set #m.r1_grotto le.vt 0
execute unless score #o.r1_grotto le.vt matches 1 run scoreboard players set #m2.r1_grotto le.vt 0
execute unless score #o.r1_grotto le.vt matches 1 run scoreboard players set #a.r1_grotto le.vt 0
execute unless score #o.r1_grotto le.vt matches 1 run scoreboard players set #e.r1_grotto le.vt 0
execute unless score #o.r1_tower le.vt matches 1 run scoreboard players set #m.r1_tower le.vt 0
execute unless score #o.r1_tower le.vt matches 1 run scoreboard players set #m2.r1_tower le.vt 0
execute unless score #o.r1_tower le.vt matches 1 run scoreboard players set #a.r1_tower le.vt 0
execute unless score #o.r1_tower le.vt matches 1 run scoreboard players set #e.r1_tower le.vt 0
# 2. what is already taken (opened treasuries, the start staffs, fixed by a region task) is not laid out again
scoreboard players set #u.1 le.vt 0
scoreboard players set #u.2 le.vt 0
scoreboard players set #u.3 le.vt 0
scoreboard players set #u.4 le.vt 0
scoreboard players set #u.5 le.vt 0
scoreboard players set #u.6 le.vt 0
scoreboard players set #u.7 le.vt 0
scoreboard players set #u.8 le.vt 0
scoreboard players set #u.9 le.vt 0
scoreboard players set #u.10 le.vt 0
scoreboard players set #u.11 le.vt 0
scoreboard players set #u.12 le.vt 0
scoreboard players set #u.13 le.vt 0
execute if score #o.r1_ogre le.vt matches 1 if score #m.r1_ogre le.vt matches 1 run scoreboard players set #u.1 le.vt 1
execute if score #o.r1_ogre le.vt matches 1 if score #m.r1_ogre le.vt matches 2 run scoreboard players set #u.2 le.vt 1
execute if score #o.r1_ogre le.vt matches 1 if score #m.r1_ogre le.vt matches 3 run scoreboard players set #u.3 le.vt 1
execute if score #o.r1_ogre le.vt matches 1 if score #m.r1_ogre le.vt matches 4 run scoreboard players set #u.4 le.vt 1
execute if score #o.r1_ogre le.vt matches 1 if score #m.r1_ogre le.vt matches 5 run scoreboard players set #u.5 le.vt 1
execute if score #o.r1_ogre le.vt matches 1 if score #m.r1_ogre le.vt matches 6 run scoreboard players set #u.6 le.vt 1
execute if score #o.r1_ogre le.vt matches 1 if score #m.r1_ogre le.vt matches 7 run scoreboard players set #u.7 le.vt 1
execute if score #o.r1_ogre le.vt matches 1 if score #m.r1_ogre le.vt matches 8 run scoreboard players set #u.8 le.vt 1
execute if score #o.r1_ogre le.vt matches 1 if score #m.r1_ogre le.vt matches 9 run scoreboard players set #u.9 le.vt 1
execute if score #o.r1_ogre le.vt matches 1 if score #m.r1_ogre le.vt matches 10 run scoreboard players set #u.10 le.vt 1
execute if score #o.r1_ogre le.vt matches 1 if score #m.r1_ogre le.vt matches 11 run scoreboard players set #u.11 le.vt 1
execute if score #o.r1_ogre le.vt matches 1 if score #m.r1_ogre le.vt matches 12 run scoreboard players set #u.12 le.vt 1
execute if score #o.r1_ogre le.vt matches 1 if score #m.r1_ogre le.vt matches 13 run scoreboard players set #u.13 le.vt 1
execute if score #o.r1_ogre le.vt matches 1 if score #m2.r1_ogre le.vt matches 1 run scoreboard players set #u.1 le.vt 1
execute if score #o.r1_ogre le.vt matches 1 if score #m2.r1_ogre le.vt matches 2 run scoreboard players set #u.2 le.vt 1
execute if score #o.r1_ogre le.vt matches 1 if score #m2.r1_ogre le.vt matches 3 run scoreboard players set #u.3 le.vt 1
execute if score #o.r1_ogre le.vt matches 1 if score #m2.r1_ogre le.vt matches 4 run scoreboard players set #u.4 le.vt 1
execute if score #o.r1_ogre le.vt matches 1 if score #m2.r1_ogre le.vt matches 5 run scoreboard players set #u.5 le.vt 1
execute if score #o.r1_ogre le.vt matches 1 if score #m2.r1_ogre le.vt matches 6 run scoreboard players set #u.6 le.vt 1
execute if score #o.r1_ogre le.vt matches 1 if score #m2.r1_ogre le.vt matches 7 run scoreboard players set #u.7 le.vt 1
execute if score #o.r1_ogre le.vt matches 1 if score #m2.r1_ogre le.vt matches 8 run scoreboard players set #u.8 le.vt 1
execute if score #o.r1_ogre le.vt matches 1 if score #m2.r1_ogre le.vt matches 9 run scoreboard players set #u.9 le.vt 1
execute if score #o.r1_ogre le.vt matches 1 if score #m2.r1_ogre le.vt matches 10 run scoreboard players set #u.10 le.vt 1
execute if score #o.r1_ogre le.vt matches 1 if score #m2.r1_ogre le.vt matches 11 run scoreboard players set #u.11 le.vt 1
execute if score #o.r1_ogre le.vt matches 1 if score #m2.r1_ogre le.vt matches 12 run scoreboard players set #u.12 le.vt 1
execute if score #o.r1_ogre le.vt matches 1 if score #m2.r1_ogre le.vt matches 13 run scoreboard players set #u.13 le.vt 1
execute if score #o.r1_grotto le.vt matches 1 if score #m.r1_grotto le.vt matches 1 run scoreboard players set #u.1 le.vt 1
execute if score #o.r1_grotto le.vt matches 1 if score #m.r1_grotto le.vt matches 2 run scoreboard players set #u.2 le.vt 1
execute if score #o.r1_grotto le.vt matches 1 if score #m.r1_grotto le.vt matches 3 run scoreboard players set #u.3 le.vt 1
execute if score #o.r1_grotto le.vt matches 1 if score #m.r1_grotto le.vt matches 4 run scoreboard players set #u.4 le.vt 1
execute if score #o.r1_grotto le.vt matches 1 if score #m.r1_grotto le.vt matches 5 run scoreboard players set #u.5 le.vt 1
execute if score #o.r1_grotto le.vt matches 1 if score #m.r1_grotto le.vt matches 6 run scoreboard players set #u.6 le.vt 1
execute if score #o.r1_grotto le.vt matches 1 if score #m.r1_grotto le.vt matches 7 run scoreboard players set #u.7 le.vt 1
execute if score #o.r1_grotto le.vt matches 1 if score #m.r1_grotto le.vt matches 8 run scoreboard players set #u.8 le.vt 1
execute if score #o.r1_grotto le.vt matches 1 if score #m.r1_grotto le.vt matches 9 run scoreboard players set #u.9 le.vt 1
execute if score #o.r1_grotto le.vt matches 1 if score #m.r1_grotto le.vt matches 10 run scoreboard players set #u.10 le.vt 1
execute if score #o.r1_grotto le.vt matches 1 if score #m.r1_grotto le.vt matches 11 run scoreboard players set #u.11 le.vt 1
execute if score #o.r1_grotto le.vt matches 1 if score #m.r1_grotto le.vt matches 12 run scoreboard players set #u.12 le.vt 1
execute if score #o.r1_grotto le.vt matches 1 if score #m.r1_grotto le.vt matches 13 run scoreboard players set #u.13 le.vt 1
execute if score #o.r1_grotto le.vt matches 1 if score #m2.r1_grotto le.vt matches 1 run scoreboard players set #u.1 le.vt 1
execute if score #o.r1_grotto le.vt matches 1 if score #m2.r1_grotto le.vt matches 2 run scoreboard players set #u.2 le.vt 1
execute if score #o.r1_grotto le.vt matches 1 if score #m2.r1_grotto le.vt matches 3 run scoreboard players set #u.3 le.vt 1
execute if score #o.r1_grotto le.vt matches 1 if score #m2.r1_grotto le.vt matches 4 run scoreboard players set #u.4 le.vt 1
execute if score #o.r1_grotto le.vt matches 1 if score #m2.r1_grotto le.vt matches 5 run scoreboard players set #u.5 le.vt 1
execute if score #o.r1_grotto le.vt matches 1 if score #m2.r1_grotto le.vt matches 6 run scoreboard players set #u.6 le.vt 1
execute if score #o.r1_grotto le.vt matches 1 if score #m2.r1_grotto le.vt matches 7 run scoreboard players set #u.7 le.vt 1
execute if score #o.r1_grotto le.vt matches 1 if score #m2.r1_grotto le.vt matches 8 run scoreboard players set #u.8 le.vt 1
execute if score #o.r1_grotto le.vt matches 1 if score #m2.r1_grotto le.vt matches 9 run scoreboard players set #u.9 le.vt 1
execute if score #o.r1_grotto le.vt matches 1 if score #m2.r1_grotto le.vt matches 10 run scoreboard players set #u.10 le.vt 1
execute if score #o.r1_grotto le.vt matches 1 if score #m2.r1_grotto le.vt matches 11 run scoreboard players set #u.11 le.vt 1
execute if score #o.r1_grotto le.vt matches 1 if score #m2.r1_grotto le.vt matches 12 run scoreboard players set #u.12 le.vt 1
execute if score #o.r1_grotto le.vt matches 1 if score #m2.r1_grotto le.vt matches 13 run scoreboard players set #u.13 le.vt 1
execute if score #o.r1_tower le.vt matches 1 if score #m.r1_tower le.vt matches 1 run scoreboard players set #u.1 le.vt 1
execute if score #o.r1_tower le.vt matches 1 if score #m.r1_tower le.vt matches 2 run scoreboard players set #u.2 le.vt 1
execute if score #o.r1_tower le.vt matches 1 if score #m.r1_tower le.vt matches 3 run scoreboard players set #u.3 le.vt 1
execute if score #o.r1_tower le.vt matches 1 if score #m.r1_tower le.vt matches 4 run scoreboard players set #u.4 le.vt 1
execute if score #o.r1_tower le.vt matches 1 if score #m.r1_tower le.vt matches 5 run scoreboard players set #u.5 le.vt 1
execute if score #o.r1_tower le.vt matches 1 if score #m.r1_tower le.vt matches 6 run scoreboard players set #u.6 le.vt 1
execute if score #o.r1_tower le.vt matches 1 if score #m.r1_tower le.vt matches 7 run scoreboard players set #u.7 le.vt 1
execute if score #o.r1_tower le.vt matches 1 if score #m.r1_tower le.vt matches 8 run scoreboard players set #u.8 le.vt 1
execute if score #o.r1_tower le.vt matches 1 if score #m.r1_tower le.vt matches 9 run scoreboard players set #u.9 le.vt 1
execute if score #o.r1_tower le.vt matches 1 if score #m.r1_tower le.vt matches 10 run scoreboard players set #u.10 le.vt 1
execute if score #o.r1_tower le.vt matches 1 if score #m.r1_tower le.vt matches 11 run scoreboard players set #u.11 le.vt 1
execute if score #o.r1_tower le.vt matches 1 if score #m.r1_tower le.vt matches 12 run scoreboard players set #u.12 le.vt 1
execute if score #o.r1_tower le.vt matches 1 if score #m.r1_tower le.vt matches 13 run scoreboard players set #u.13 le.vt 1
execute if score #o.r1_tower le.vt matches 1 if score #m2.r1_tower le.vt matches 1 run scoreboard players set #u.1 le.vt 1
execute if score #o.r1_tower le.vt matches 1 if score #m2.r1_tower le.vt matches 2 run scoreboard players set #u.2 le.vt 1
execute if score #o.r1_tower le.vt matches 1 if score #m2.r1_tower le.vt matches 3 run scoreboard players set #u.3 le.vt 1
execute if score #o.r1_tower le.vt matches 1 if score #m2.r1_tower le.vt matches 4 run scoreboard players set #u.4 le.vt 1
execute if score #o.r1_tower le.vt matches 1 if score #m2.r1_tower le.vt matches 5 run scoreboard players set #u.5 le.vt 1
execute if score #o.r1_tower le.vt matches 1 if score #m2.r1_tower le.vt matches 6 run scoreboard players set #u.6 le.vt 1
execute if score #o.r1_tower le.vt matches 1 if score #m2.r1_tower le.vt matches 7 run scoreboard players set #u.7 le.vt 1
execute if score #o.r1_tower le.vt matches 1 if score #m2.r1_tower le.vt matches 8 run scoreboard players set #u.8 le.vt 1
execute if score #o.r1_tower le.vt matches 1 if score #m2.r1_tower le.vt matches 9 run scoreboard players set #u.9 le.vt 1
execute if score #o.r1_tower le.vt matches 1 if score #m2.r1_tower le.vt matches 10 run scoreboard players set #u.10 le.vt 1
execute if score #o.r1_tower le.vt matches 1 if score #m2.r1_tower le.vt matches 11 run scoreboard players set #u.11 le.vt 1
execute if score #o.r1_tower le.vt matches 1 if score #m2.r1_tower le.vt matches 12 run scoreboard players set #u.12 le.vt 1
execute if score #o.r1_tower le.vt matches 1 if score #m2.r1_tower le.vt matches 13 run scoreboard players set #u.13 le.vt 1
execute if score #st.1 le.vt matches 1 run scoreboard players set #u.1 le.vt 1
execute if score #st.2 le.vt matches 1 run scoreboard players set #u.2 le.vt 1
execute if score #st.3 le.vt matches 1 run scoreboard players set #u.3 le.vt 1
execute if score #st.4 le.vt matches 1 run scoreboard players set #u.4 le.vt 1
execute if score #st.5 le.vt matches 1 run scoreboard players set #u.5 le.vt 1
# 3. fixed main items of the region tasks
# 4. single items, pairs, the staffs over the regions
scoreboard players set #k le.vt 13
execute unless score #u.13 le.vt matches 1 run function last_ember:vault/gen/put_1
scoreboard players set #k le.vt 6
execute unless score #u.6 le.vt matches 1 run function last_ember:vault/gen/put_2
execute store result score #c le.vt run random value 0..1
execute if score #c le.vt matches 0 run function last_ember:vault/gen/pair_7_8_0
execute if score #c le.vt matches 1 run function last_ember:vault/gen/pair_7_8_1
execute store result score #c le.vt run random value 0..1
execute if score #c le.vt matches 0 run function last_ember:vault/gen/pair_11_12_0
execute if score #c le.vt matches 1 run function last_ember:vault/gen/pair_11_12_1
execute store result score #c le.vt run random value 0..1
execute if score #c le.vt matches 0 run function last_ember:vault/gen/pair_9_10_0
execute if score #c le.vt matches 1 run function last_ember:vault/gen/pair_9_10_1
scoreboard players set #p.1 le.vt 0
scoreboard players set #p.2 le.vt 0
scoreboard players set #p.3 le.vt 0
scoreboard players set #p.4 le.vt 0
scoreboard players set #p.5 le.vt 0
function last_ember:vault/gen/ch_3
function last_ember:vault/gen/ch_4
function last_ember:vault/gen/ch_5
function last_ember:vault/gen/ch_6
function last_ember:vault/gen/ch_7
# 5. one golden apple per region, one grimoire of Mending in the game (Р6)
scoreboard players set #had le.vt 0
execute if score #o.r1_ogre le.vt matches 1 if score #a.r1_ogre le.vt matches 1 run scoreboard players set #had le.vt 1
execute if score #o.r1_grotto le.vt matches 1 if score #a.r1_grotto le.vt matches 1 run scoreboard players set #had le.vt 1
execute if score #o.r1_tower le.vt matches 1 if score #a.r1_tower le.vt matches 1 run scoreboard players set #had le.vt 1
execute if score #had le.vt matches 0 run function last_ember:vault/gen/ch_8
# 6. treasuries left without a main item: the filler (the best book of the region and ingots x2)
execute unless score #o.r1_ogre le.vt matches 1 if score #m.r1_ogre le.vt matches 0 run scoreboard players set #m.r1_ogre le.vt 99
execute unless score #o.r1_grotto le.vt matches 1 if score #m.r1_grotto le.vt matches 0 run scoreboard players set #m.r1_grotto le.vt 99
execute unless score #o.r1_tower le.vt matches 1 if score #m.r1_tower le.vt matches 0 run scoreboard players set #m.r1_tower le.vt 99
