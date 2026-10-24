# the sound of the moment dig of the scolopendra (fish): the variant is #v_fish le.l (1-3, lab/voice)
execute if score #v_fish le.l matches 2 run playsound last_ember:creature.endrega.exp_digging hostile @a ~ ~1.5 ~ 1.8 1
execute if score #v_fish le.l matches 3 run playsound last_ember:creature.endrega.exp_digging hostile @a ~ ~1.5 ~ 1.0 1
execute if score #v_fish le.l matches 2..3 run return 0
playsound last_ember:creature.scolopendromorph.movement_digging hostile @a ~ ~1.5 ~ 1.8 1
