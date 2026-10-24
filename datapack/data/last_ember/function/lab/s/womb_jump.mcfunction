# the sound of the moment jump of the womb: the variant is #v_womb le.l (1-3, lab/voice)
execute if score #v_womb le.l matches 2 run playsound last_ember:creature.rotfiend.vo_breathin hostile @a ~ ~ ~ 1.0 1
execute if score #v_womb le.l matches 3 run playsound last_ember:creature.archespor.movement_whoosh_small hostile @a ~ ~ ~ 1.0 1
execute if score #v_womb le.l matches 2..3 run return 0
playsound last_ember:creature.toad.mv_jump hostile @a ~ ~ ~ 1.0 1
