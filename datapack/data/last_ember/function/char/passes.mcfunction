# soft passages: no people -- no way to the Font, no class -- no way to the stairs (a gentle push back, no damage)
execute as @a[scores={le.race=0},gamemode=!spectator,gamemode=!creative] if entity @s[x=-18,y=50,z=45.5,dx=36,dy=30,dz=30] run function last_ember:char/push_race
execute as @a[scores={le.race=1..,le.class=0},gamemode=!spectator,gamemode=!creative] if entity @s[x=14.5,y=50,z=17,dx=40,dy=50,dz=45] run function last_ember:char/push_class
execute as @a[scores={le.race=1..,le.class=0},gamemode=!spectator,gamemode=!creative] if entity @s[x=-8,y=94,z=11,dx=22,dy=10,dz=30] run function last_ember:char/push_class
