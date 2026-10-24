# the sound of the moment rumble of the scolopendra (fish): the variant is #v_fish le.l (1-3, lab/voice)
execute if score #v_fish le.l matches 2 run playsound last_ember:creature.endrega.mv_stomp hostile @a ~ ~1.5 ~ 1.3 1
execute if score #v_fish le.l matches 3 run playsound last_ember:creature.crabs.crab_footsteps hostile @a ~ ~1.5 ~ 0.9 1
execute if score #v_fish le.l matches 2..3 run return 0
playsound last_ember:creature.scolopendromorph.combat_underground_mouvement hostile @a ~ ~1.5 ~ 1.4 1
