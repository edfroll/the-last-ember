# T-027: the key is carried (#ks 1): lost -> back into Thane's coffin (the lid closes, it can be opened again)
function last_ember:cemetery/lost {key:"crypt_key",state:"ks",to:0}
execute if score #ks le.cem matches 0 run function last_ember:cemetery/gen/lid_close
