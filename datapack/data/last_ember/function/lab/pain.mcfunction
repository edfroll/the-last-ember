# hurt (the health went down): a cry not more often than every 0.6 s; the models of the display samples flash red
execute if score @s le.lpc matches 1.. run return 0
scoreboard players set @s le.lpc 12
execute if entity @s[tag=le.lab_drowner] run playsound last_ember:creature.drowner.uw_pain hostile @a ~ ~ ~ 1.8 1
execute if entity @s[tag=le.lab_warg] run playsound last_ember:creature.wild_dog.pain hostile @a ~ ~ ~ 1.8 1
execute if entity @s[tag=le.lab_womb] run function last_ember:lab/s/womb_pain
execute if entity @s[tag=le.lab_leshy] run playsound last_ember:creature.leshen.vo_pain_light hostile @a ~ ~ ~ 1.8 1
execute if entity @s[tag=le.lab_fish] run function last_ember:lab/s/fish_pain
execute if entity @s[tag=le.lab_womb] run function last_ember:lab/flash_on
execute if entity @s[tag=le.lab_leshy] run function last_ember:lab/flash_on
