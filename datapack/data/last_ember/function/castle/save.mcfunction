# T-028: the state into storage (restored by castle/gen/init when the scoreboard is lost)
execute store result storage last_ember:castle st.faded int 1 run scoreboard players get #faded le.cas
execute store result storage last_ember:castle st.amb int 1 run scoreboard players get #amb le.cas
execute store result storage last_ember:castle st.ambt int 1 run scoreboard players get #ambt le.cas
