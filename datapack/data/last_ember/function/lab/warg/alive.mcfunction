function last_ember:lab/turn
# close to its prey it turns its muzzle to it (the big wolf turns its body slowly and could bite with its back)
execute if entity @a[distance=..4.5,gamemode=!spectator,gamemode=!creative] run rotate @s facing entity @p[gamemode=!spectator,gamemode=!creative] feet
# always angry: at the nearest player within 32, renewed every second
execute if score #sec le.l matches 0 run function last_ember:lab/warg/anger
execute if score @s le.lcd matches ..0 if entity @a[distance=..3.5,gamemode=!spectator,gamemode=!creative] run function last_ember:lab/warg/swing
execute if score @s le.lst matches 110.. run function last_ember:lab/warg/step
