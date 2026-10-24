# the sound of the moment step of the fish: the variant is #v_fish le.l (1-3, lab/voice)
execute if score #v_fish le.l matches 2 run playsound last_ember:creature.scolopendromorph.movement_rotation hostile @a ~ ~ ~ 0.5 1
execute if score #v_fish le.l matches 3 run playsound last_ember:creature.crabs.crab_footsteps hostile @a ~ ~ ~ 0.7 1
execute if score #v_fish le.l matches 2..3 run return 0
playsound last_ember:creature.endrega.mv_footsteps.most_surfaces_22 hostile @a ~ ~ ~ 0.6 1
