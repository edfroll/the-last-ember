# the sound of the moment pain of the fish: the variant is #v_fish le.l (1-3, lab/voice)
execute if score #v_fish le.l matches 2 run playsound last_ember:creature.scolopendromorph.combat_hit_back_scales hostile @a ~ ~ ~ 1.6 1
execute if score #v_fish le.l matches 3 run playsound last_ember:creature.rat.squeak hostile @a ~ ~ ~ 1.6 1
execute if score #v_fish le.l matches 2..3 run return 0
playsound last_ember:creature.endrega.cmb_pain hostile @a ~ ~ ~ 1.8 1
