# the sound of the moment idle2 of the womb: the variant is #v_womb le.l (1-3, lab/voice)
execute if score #v_womb le.l matches 2 run playsound last_ember:creature.rotfiend.vo_breathout hostile @a ~ ~ ~ 1.6 1
execute if score #v_womb le.l matches 3 run playsound last_ember:creature.archespor.movement_idling hostile @a ~ ~ ~ 1.4 1
execute if score #v_womb le.l matches 2..3 run return 0
playsound last_ember:creature.water_hag.vo_gurgle_short hostile @a ~ ~ ~ 1.8 1
