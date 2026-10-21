execute if entity @a[distance=..8,tag=!le.healer_self,scores={le.hp=1}] run return run function last_ember:potion/amulet_give {v:1}
execute if entity @a[distance=..8,tag=!le.healer_self,scores={le.hp=2}] run return run function last_ember:potion/amulet_give {v:2}
execute if entity @a[distance=..8,tag=!le.healer_self,scores={le.hp=3}] run return run function last_ember:potion/amulet_give {v:3}
execute if entity @a[distance=..8,tag=!le.healer_self,scores={le.hp=4}] run return run function last_ember:potion/amulet_give {v:4}
execute if entity @a[distance=..8,tag=!le.healer_self,scores={le.hp=5}] run function last_ember:potion/amulet_give {v:5}
