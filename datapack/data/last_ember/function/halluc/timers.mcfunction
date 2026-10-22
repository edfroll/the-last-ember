# as a player (stage in #st le.h >= 1): the countdowns of the events; a timer that has run out fires its event and is set again (a new one is only set, never fired at once)
# whisper: stage 1 every 60-120 s, 2-3 every 30-60 s, 4 every 15-30 s
execute unless score @s le.hw matches -2147483648..2147483647 run function last_ember:halluc/roll_w
execute store success score #fire le.h if score @s le.hw matches ..0
execute if score #fire le.h matches 1 run function last_ember:halluc/whisper
execute if score #fire le.h matches 1 run function last_ember:halluc/roll_w
scoreboard players remove @s le.hw 20
# shadows and false mobs: stage 2+
execute if score #st le.h matches 2.. run function last_ember:halluc/timers_2
# pulses: stage 3+
execute if score #st le.h matches 3.. run function last_ember:halluc/timers_3
# blows: stage 4
execute if score #st le.h matches 4.. run function last_ember:halluc/timers_4
