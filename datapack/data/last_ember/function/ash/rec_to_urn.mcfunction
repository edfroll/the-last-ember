# storage last_ember:dt rec -> its urn (lava / void / no free spot)
execute if data storage last_ember:dt {urn:"none"} run data modify storage last_ember:dt rec.urn set value "r0"
function last_ember:urn/add with storage last_ember:dt rec
tellraw @s {"text":"Ваш пепел не найти на месте гибели: вещи ушли в Урну Утраченного.","color":"gray","italic":true}
