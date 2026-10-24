# the sound of the moment hit of the scolopendra (fish): the variant is #v_fish le.l (1-3, lab/voice)
execute if score #v_fish le.l matches 2 run playsound last_ember:creature.endrega.cmb_attack hostile @a ~ ~1 ~ 1.4 1
execute if score #v_fish le.l matches 3 run playsound last_ember:creature.crabs.crab_shell hostile @a ~ ~1 ~ 1.2 1
execute if score #v_fish le.l matches 2..3 run return 0
playsound last_ember:creature.scolopendromorph.combat_hit hostile @a ~ ~1 ~ 1.4 1
