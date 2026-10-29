# as a sample at itself, every tick
# T-020: a monster of a contract first goes through its contract (the blows, the leash, its own dormant states)
execute if entity @s[tag=le.contract] if function last_ember:contract/m/tick run return 0
execute if score @s le.ls matches 0 run return run function last_ember:lab/dormant
execute if score @s le.ls matches 1 run return run function last_ember:lab/appear
execute if score @s le.ls matches 3 run return run function last_ember:lab/dying
execute if score @s le.ls matches 5 run return run function last_ember:lab/fish/under
# alive: the health is the real one + 500 (lab/<kind>/spawn); at 500 it is dead by our rules and dies its own way, never the vanilla way
execute store result score #hp le.l run data get entity @s Health
execute if score #hp le.l matches ..500 run return run function last_ember:lab/die
execute if score #hp le.l < @s le.lhp run function last_ember:lab/pain
scoreboard players operation @s le.lhp = #hp le.l
function last_ember:lab/move
scoreboard players remove @s le.lid 1
execute if score @s le.lid matches ..0 run function last_ember:lab/idle
scoreboard players remove @s le.lcd 1
scoreboard players remove @s le.lpc 1
execute if score @s le.lfl matches 1.. run function last_ember:lab/flash_tick
execute if entity @s[tag=le.lab_drowner] run return run function last_ember:lab/drowner/alive
execute if entity @s[tag=le.lab_warg] run return run function last_ember:lab/warg/alive
execute if entity @s[tag=le.lab_womb] run return run function last_ember:lab/womb/alive
execute if entity @s[tag=le.lab_leshy] run return run function last_ember:lab/leshy/alive
execute if entity @s[tag=le.lab_fish] run return run function last_ember:lab/fish/alive
