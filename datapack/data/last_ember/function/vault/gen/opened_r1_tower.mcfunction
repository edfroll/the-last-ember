# a player generated the loot of the treasury r1_tower: it is open, its main items are taken
advancement revoke @s only last_ember:vault/open_r1_tower
scoreboard players set #o.r1_tower le.vt 1
execute if score #m.r1_tower le.vt matches 1 run scoreboard players set #st.1 le.vt 1
execute if score #m2.r1_tower le.vt matches 1 run scoreboard players set #st.1 le.vt 1
execute if score #m.r1_tower le.vt matches 2 run scoreboard players set #st.2 le.vt 1
execute if score #m2.r1_tower le.vt matches 2 run scoreboard players set #st.2 le.vt 1
execute if score #m.r1_tower le.vt matches 3 run scoreboard players set #st.3 le.vt 1
execute if score #m2.r1_tower le.vt matches 3 run scoreboard players set #st.3 le.vt 1
execute if score #m.r1_tower le.vt matches 4 run scoreboard players set #st.4 le.vt 1
execute if score #m2.r1_tower le.vt matches 4 run scoreboard players set #st.4 le.vt 1
execute if score #m.r1_tower le.vt matches 5 run scoreboard players set #st.5 le.vt 1
execute if score #m2.r1_tower le.vt matches 5 run scoreboard players set #st.5 le.vt 1
