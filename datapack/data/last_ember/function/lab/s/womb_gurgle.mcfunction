# the sound of the moment gurgle of the womb: the variant is #v_womb le.l (1-3, lab/voice)
execute if score #v_womb le.l matches 2 run playsound last_ember:creature.toad.vo_resonance_soft hostile @a ~ ~ ~ 1.8 1
execute if score #v_womb le.l matches 3 run playsound last_ember:creature.archespor.combat_hides hostile @a ~ ~ ~ 1.6 1
execute if score #v_womb le.l matches 2..3 run return 0
playsound last_ember:creature.rotfiend.uw_movement_heavy hostile @a ~ ~ ~ 1.8 1
