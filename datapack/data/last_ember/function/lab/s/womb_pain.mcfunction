# the sound of the moment pain of the womb: the variant is #v_womb le.l (1-3, lab/voice)
execute if score #v_womb le.l matches 2 run playsound last_ember:creature.toad.vo_pain hostile @a ~ ~ ~ 1.8 1
execute if score #v_womb le.l matches 3 run playsound last_ember:creature.archespor.voice_hit hostile @a ~ ~ ~ 1.8 1
execute if score #v_womb le.l matches 2..3 run return 0
playsound last_ember:creature.rotfiend.vo_dmg hostile @a ~ ~ ~ 1.8 1
