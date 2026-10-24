# the sound of the moment death of the fish: the variant is #v_fish le.l (1-3, lab/voice)
execute if score #v_fish le.l matches 2 run playsound last_ember:creature.scolopendromorph.combat_death hostile @a ~ ~ ~ 1.8 1
execute if score #v_fish le.l matches 3 run playsound last_ember:creature.crabs.dying hostile @a ~ ~ ~ 1.4 1
execute if score #v_fish le.l matches 3 run playsound last_ember:creature.rat.death_impact hostile @a ~ ~ ~ 1.2 1
execute if score #v_fish le.l matches 2..3 run return 0
playsound last_ember:creature.endrega.cmb_death_long hostile @a ~ ~ ~ 1.8 1
