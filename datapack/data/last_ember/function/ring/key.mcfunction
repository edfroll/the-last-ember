# as a player: storage last_ember:ring u = {a,b,c,d (the UUID ints), k "a_b_c_d"}; the macro argument of everything per player
execute store result storage last_ember:ring u.a int 1 run data get entity @s UUID[0]
execute store result storage last_ember:ring u.b int 1 run data get entity @s UUID[1]
execute store result storage last_ember:ring u.c int 1 run data get entity @s UUID[2]
execute store result storage last_ember:ring u.d int 1 run data get entity @s UUID[3]
function last_ember:ring/key_m with storage last_ember:ring u
