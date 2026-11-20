# T-027: the key still in Thane's coffin (#ks 0): a player picked it up -> carried; the first time the quest is at «key found»
execute store result score #c le.cem run clear @a *[minecraft:custom_data~{le_citem:"crypt_key"}] 0
execute if score #c le.cem matches 0 run return 0
scoreboard players set #ks le.cem 1
execute if score #q le.cem matches ..1 run scoreboard players set #q le.cem 2
function last_ember:cemetery/save
