execute if score @s le.race matches ..0 run return run title @s actionbar {"text":"Сначала выбери народ","color":"gray"}
execute if score @s le.class matches 1.. run return run function last_ember:char/chosen_class
execute if score @s le.pend = #id le.e if score @s le.pendt >= #gt le.e run return run function last_ember:char/do_class
scoreboard players operation @s le.pend = #id le.e
scoreboard players operation @s le.pendt = #gt le.e
scoreboard players add @s le.pendt 200
function last_ember:char/gen/class_desc
