# the layout of the main items over the treasuries (at the first start, after a change of the treasury list, vault/relayout); opened treasuries keep theirs
# 1. not opened treasuries: empty
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
function last_ember:vault/gen/ch_1
function last_ember:vault/gen/ch_2
function last_ember:vault/gen/ch_3
function last_ember:vault/gen/ch_4
function last_ember:vault/gen/ch_5
# 5. one golden apple per region, one grimoire of Mending in the game (Р6)
# 6. treasuries left without a main item: the filler (the best book of the region and ingots x2)
