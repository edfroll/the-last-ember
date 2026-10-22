# as a trader: the deals and what is left of them, to @a[tag=le.stk]
tellraw @a[tag=le.stk] [{"text":"Сделки торговца ","color":"gold"},{"selector":"@s"}]
execute if data entity @s Offers.Recipes[0] run function last_ember:trader/show_one {i:0}
execute if data entity @s Offers.Recipes[1] run function last_ember:trader/show_one {i:1}
execute if data entity @s Offers.Recipes[2] run function last_ember:trader/show_one {i:2}
execute if data entity @s Offers.Recipes[3] run function last_ember:trader/show_one {i:3}
execute if data entity @s Offers.Recipes[4] run function last_ember:trader/show_one {i:4}
execute if data entity @s Offers.Recipes[5] run function last_ember:trader/show_one {i:5}
execute if data entity @s Offers.Recipes[6] run function last_ember:trader/show_one {i:6}
execute if data entity @s Offers.Recipes[7] run function last_ember:trader/show_one {i:7}
execute if data entity @s Offers.Recipes[8] run function last_ember:trader/show_one {i:8}
execute if data entity @s Offers.Recipes[9] run function last_ember:trader/show_one {i:9}
execute if data entity @s Offers.Recipes[10] run function last_ember:trader/show_one {i:10}
execute if data entity @s Offers.Recipes[11] run function last_ember:trader/show_one {i:11}
