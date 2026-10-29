# as the grove leshy: 0 dormant = a tree among the trees until someone comes within 4 blocks or hits it; 1 = it tears itself out (our own wake); 1 returned = the lab skips
execute if score @s le.ls matches 2.. run return 0
execute if score @s le.ls matches 1 run return run function last_ember:contract/k/grove_leshy/wake
execute if score #hurt le.ct matches 1 run function last_ember:contract/k/grove_leshy/wake_start
execute if entity @a[gamemode=!spectator,gamemode=!creative,distance=..4] run function last_ember:contract/k/grove_leshy/wake_start
return 1
