execute store result score @s le.lid run random value 90..180
execute store result score #r le.l run random value 0..2
execute if entity @s[tag=le.lab_drowner] run return run function last_ember:lab/drowner/idle
execute if entity @s[tag=le.lab_warg] run return run function last_ember:lab/warg/idle
execute if entity @s[tag=le.lab_womb] run return run function last_ember:lab/womb/idle
execute if entity @s[tag=le.lab_leshy] run return run function last_ember:lab/leshy/idle
execute if entity @s[tag=le.lab_fish] run return run function last_ember:lab/fish/idle
