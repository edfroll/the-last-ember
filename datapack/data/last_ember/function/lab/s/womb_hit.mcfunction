# the sound of the moment hit of the womb: the variant is #v_womb le.l (1-3, lab/voice)
execute if score #v_womb le.l matches 2 run playsound last_ember:creature.rotfiend.uw_hit hostile @a ~ ~1 ~ 1.2 1
execute if score #v_womb le.l matches 3 run playsound last_ember:creature.archespor.combat_attack hostile @a ~ ~1 ~ 1.2 1
execute if score #v_womb le.l matches 2..3 run return 0
playsound last_ember:creature.toad.fx_mucus_hit hostile @a ~ ~1 ~ 1.2 1
