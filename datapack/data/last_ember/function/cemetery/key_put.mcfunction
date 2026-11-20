# T-027: Thane's lid is open and the coffin is empty, the key is nowhere: it lies in the coffin (the current generation)
data modify storage last_ember:cemetery tmp set value {key:"crypt_key"}
function last_ember:fens/count with storage last_ember:cemetery tmp
execute if score #c le.fn matches 1.. run return 0
function last_ember:cemetery/gen/key_at
