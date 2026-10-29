# as a seer at the start: #rnd le.e = a staff 1..5 that nobody has taken yet (else any); it is taken, its closed treasury gets the filler instead
scoreboard players set #rnd le.e 0
function last_ember:vault/gen/ch_6
execute if score #rnd le.e matches 0 store result score #rnd le.e run random value 1..5
execute if score #rnd le.e matches 1 run scoreboard players set #st.1 le.vt 1
execute if score #rnd le.e matches 2 run scoreboard players set #st.2 le.vt 1
execute if score #rnd le.e matches 3 run scoreboard players set #st.3 le.vt 1
execute if score #rnd le.e matches 4 run scoreboard players set #st.4 le.vt 1
execute if score #rnd le.e matches 5 run scoreboard players set #st.5 le.vt 1
