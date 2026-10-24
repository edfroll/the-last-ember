# the sound of the moment swing of the scolopendra (fish): the variant is #v_fish le.l (1-3, lab/voice)
execute if score #v_fish le.l matches 2 run playsound last_ember:creature.endrega.cmb_preattack_growl hostile @a ~ ~ ~ 1.8 1
execute if score #v_fish le.l matches 2 run playsound last_ember:creature.endrega.cmb_attack_swoosh hostile @a ~ ~ ~ 1.0 1
execute if score #v_fish le.l matches 3 run playsound last_ember:creature.crabs.attacking hostile @a ~ ~ ~ 1.2 1
execute if score #v_fish le.l matches 2..3 run return 0
playsound last_ember:creature.scolopendromorph.combat_preattack hostile @a ~ ~ ~ 1.8 1
playsound last_ember:creature.scolopendromorph.movement_whoosh_novoice hostile @a ~ ~ ~ 1.0 1
