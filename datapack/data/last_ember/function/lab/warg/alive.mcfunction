function last_ember:lab/turn
# close to its prey it turns its muzzle to it
execute if entity @a[distance=..4.5,gamemode=!spectator,gamemode=!creative] run rotate @s facing entity @p[gamemode=!spectator,gamemode=!creative] feet
# always angry: at the nearest player within 32, renewed every second
execute if score #sec le.l matches 0 run function last_ember:lab/warg/anger
scoreboard players add @s le.lt 1
scoreboard players operation #t5 le.l = @s le.lt
scoreboard players operation #t5 le.l %= #5 le.l
execute if score #t5 le.l matches 0 run function last_ember:lab/look
# the animation: 3 = in the air (stretched), 2 = biting, 1 = galloping, 0 = standing
execute store result score #og le.l run data get entity @s OnGround
execute if score #og le.l matches 0 unless score @s le.lan matches 2..3 run function last_ember:lab/warg/mode {m:3,p:"leap",d:3}
execute if score #og le.l matches 1 if score @s le.lan matches 3 run function last_ember:lab/warg/mode {m:0,p:"idle0",d:3}
execute if score @s le.lan matches 3 run return 0
execute if score @s le.lan matches 2 run return run function last_ember:lab/warg/bite
# it keeps its muzzle in front of the prey: closer than 2.3 blocks it backs off (so the player sees the maw, not its back)
execute if entity @a[distance=..2.3,gamemode=!spectator,gamemode=!creative] run function last_ember:lab/warg/back_off
execute if score @s le.lcd matches ..0 if entity @a[distance=..3.8,gamemode=!spectator,gamemode=!creative] run return run function last_ember:lab/warg/bite_start
execute if score @s le.lsp matches 6.. if score @s le.lan matches 0 run function last_ember:lab/warg/mode {m:1,p:"run1",d:2}
execute if score @s le.lsp matches ..3 if score @s le.lan matches 1 run function last_ember:lab/warg/mode {m:0,p:"idle0",d:6}
scoreboard players remove @s le.lfd 1
execute if score @s le.lfd matches ..0 if score @s le.lan matches 1 run return run function last_ember:lab/warg/run_next
execute if score @s le.lfd matches ..0 if score @s le.lan matches 0 run function last_ember:lab/warg/idle_next
