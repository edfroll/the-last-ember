execute if score #st le.h matches 1 run title @s actionbar {"text":"Глаза слипаются…","color":"gray"}
execute if score #st le.h matches 2 run title @s actionbar {"text":"Краем глаза что-то движется","color":"gray"}
execute if score #st le.h matches 3 run title @s actionbar {"text":"Земля плывёт под ногами","color":"gray"}
execute if score #st le.h matches 4 run title @s actionbar {"text":"Ты уже не помнишь, когда спал","color":"gray"}
# a new stage: the timers are set afresh (a longer wait of the old stage must not outlive the new one)
scoreboard players reset @s le.hw
scoreboard players reset @s le.hsh
scoreboard players reset @s le.hfm
scoreboard players reset @s le.hpu
scoreboard players reset @s le.hk
