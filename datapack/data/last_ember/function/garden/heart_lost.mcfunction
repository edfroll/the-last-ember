# T-025: at a destroyed heart: the players within 32 see how many are left; the last one puts the garden to sleep
function last_ember:garden/gen/count
title @a[distance=..32] actionbar [{"text":"Сердец осталось: ","color":"gray"},{"score":{"name":"#left","objective":"le.gd"},"color":"white"}]
execute if score #left le.gd matches 0 if score #asleep le.gd matches 0 run function last_ember:garden/sleep
