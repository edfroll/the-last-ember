# a staff not taken: one at random of those that fit; return 0 when none
scoreboard players set #n le.vt 0
execute unless score #st.1 le.vt matches 1 run scoreboard players add #n le.vt 1
execute unless score #st.2 le.vt matches 1 run scoreboard players add #n le.vt 1
execute unless score #st.3 le.vt matches 1 run scoreboard players add #n le.vt 1
execute unless score #st.4 le.vt matches 1 run scoreboard players add #n le.vt 1
execute unless score #st.5 le.vt matches 1 run scoreboard players add #n le.vt 1
execute if score #n le.vt matches 0 run return 0
execute store result score #r le.vt run random value 0..9999
scoreboard players operation #r le.vt %= #n le.vt
execute unless score #st.1 le.vt matches 1 run scoreboard players remove #r le.vt 1
execute if score #r le.vt matches -1 unless score #st.1 le.vt matches 1 run return run scoreboard players set #rnd le.e 1
execute unless score #st.2 le.vt matches 1 run scoreboard players remove #r le.vt 1
execute if score #r le.vt matches -1 unless score #st.2 le.vt matches 1 run return run scoreboard players set #rnd le.e 2
execute unless score #st.3 le.vt matches 1 run scoreboard players remove #r le.vt 1
execute if score #r le.vt matches -1 unless score #st.3 le.vt matches 1 run return run scoreboard players set #rnd le.e 3
execute unless score #st.4 le.vt matches 1 run scoreboard players remove #r le.vt 1
execute if score #r le.vt matches -1 unless score #st.4 le.vt matches 1 run return run scoreboard players set #rnd le.e 4
execute unless score #st.5 le.vt matches 1 run scoreboard players remove #r le.vt 1
execute if score #r le.vt matches -1 unless score #st.5 le.vt matches 1 run return run scoreboard players set #rnd le.e 5
return 0
