# T-027: every second: the shovel and the seal (lost -> the shovel at the keeper again / the seal in the sarcophagus again; old copies go)
execute if score #sh le.cem matches 1 run function last_ember:cemetery/lost {key:"cem_shovel",state:"sh",to:2}
execute if score #ss le.cem matches 2 run function last_ember:cemetery/lost {key:"seal",state:"ss",to:1}
