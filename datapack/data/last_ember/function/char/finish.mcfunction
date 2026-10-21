# as a player: people and class chosen -- the respawn point moves to the Main Bonfire
scoreboard players reset @s le.pend
scoreboard players reset @s le.pendt
function last_ember:bonfire/bind_start
title @s actionbar {"text":"Путь наверх открыт.","color":"gold"}
