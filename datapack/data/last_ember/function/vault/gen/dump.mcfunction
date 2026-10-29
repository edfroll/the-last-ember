# TEST: the layout into storage last_ember:vt d (one read for the tests)
data remove storage last_ember:vt d
execute store result storage last_ember:vt d.st1 int 1 run scoreboard players get #st.1 le.vt
execute store result storage last_ember:vt d.st2 int 1 run scoreboard players get #st.2 le.vt
execute store result storage last_ember:vt d.st3 int 1 run scoreboard players get #st.3 le.vt
execute store result storage last_ember:vt d.st4 int 1 run scoreboard players get #st.4 le.vt
execute store result storage last_ember:vt d.st5 int 1 run scoreboard players get #st.5 le.vt
