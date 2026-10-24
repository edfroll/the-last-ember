# the sound of the moment land2 of the womb: the variant is #v_womb le.l (1-3, lab/voice)
execute if score #v_womb le.l matches 2 run playsound last_ember:creature.toad.fx_stomp hostile @a ~ ~ ~ 0.9 1
execute if score #v_womb le.l matches 3 run playsound last_ember:creature.archespor.movement_blood hostile @a ~ ~ ~ 0.8 1
execute if score #v_womb le.l matches 2..3 run return 0
playsound last_ember:creature.rotfiend.mv_bodyfall hostile @a ~ ~ ~ 0.8 1
