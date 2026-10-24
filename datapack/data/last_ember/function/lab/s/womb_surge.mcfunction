# the sound of the moment surge of the womb: the variant is #v_womb le.l (1-3, lab/voice)
execute if score #v_womb le.l matches 2 run playsound last_ember:creature.toad.mv_footsteps hostile @a ~ ~ ~ 1.0 1
execute if score #v_womb le.l matches 2 run playsound last_ember:creature.toad.vo_melee hostile @a ~ ~ ~ 1.4 1
execute if score #v_womb le.l matches 3 run playsound last_ember:creature.archespor.movement_whoosh_med hostile @a ~ ~ ~ 1.0 1
execute if score #v_womb le.l matches 3 run playsound last_ember:creature.archespor.voice_stagger hostile @a ~ ~ ~ 1.4 1
execute if score #v_womb le.l matches 2..3 run return 0
playsound last_ember:creature.rotfiend.vo_breathout hostile @a ~ ~ ~ 1.6 1
playsound last_ember:creature.rotfiend.mv_flesh hostile @a ~ ~ ~ 0.9 1
