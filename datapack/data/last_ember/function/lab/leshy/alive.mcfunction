function last_ember:lab/turn
scoreboard players add @s le.lt 1
# the head looks at the nearest player (every 5 ticks; it shows with the next frame)
scoreboard players operation #t5 le.l = @s le.lt
scoreboard players operation #t5 le.l %= #5 le.l
execute if score #t5 le.l matches 0 run function last_ember:lab/look
# the attack is ours (the carrier's own attack does no harm): a swing when somebody is within 3.6 blocks
execute if score @s le.lan matches 2 run return run function last_ember:lab/leshy/attack
execute if score @s le.lcd matches ..0 if entity @a[distance=..3.6,gamemode=!spectator,gamemode=!creative] run return run function last_ember:lab/leshy/attack_start
# walking (the legs keep time with the way made) or standing (breathing)
execute if score @s le.lsp matches 4.. if score @s le.lan matches 0 run function last_ember:lab/leshy/mode {m:1}
execute if score @s le.lsp matches ..3 if score @s le.lan matches 1 run function last_ember:lab/leshy/mode {m:0}
scoreboard players remove @s le.lfd 1
execute if score @s le.lfd matches ..0 if score @s le.lan matches 1 run return run function last_ember:lab/leshy/walk_next
execute if score @s le.lfd matches ..0 if score @s le.lan matches 0 run function last_ember:lab/leshy/idle_next
