# the sound of the moment death2 of the womb: the variant is #v_womb le.l (1-3, lab/voice)
execute if score #v_womb le.l matches 2 run playsound last_ember:creature.toad.fx_vomit hostile @a ~ ~ ~ 1.4 1
execute if score #v_womb le.l matches 3 run playsound last_ember:creature.archespor.movement_death_blood_spray hostile @a ~ ~ ~ 1.4 1
execute if score #v_womb le.l matches 2..3 run return 0
playsound last_ember:creature.rotfiend.explode hostile @a ~ ~ ~ 1.6 1
