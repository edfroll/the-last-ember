# the sound of the moment death of the womb: the variant is #v_womb le.l (1-3, lab/voice)
execute if score #v_womb le.l matches 2 run playsound last_ember:creature.toad.vo_pain_heavy hostile @a ~ ~ ~ 1.8 1
execute if score #v_womb le.l matches 3 run playsound last_ember:creature.archespor.voice_death hostile @a ~ ~ ~ 1.8 1
execute if score #v_womb le.l matches 2..3 run return 0
playsound last_ember:creature.rotfiend.vo_die hostile @a ~ ~ ~ 1.8 1
