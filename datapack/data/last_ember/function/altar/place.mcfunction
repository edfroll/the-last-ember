# macro aid ch dim x y z n: registers an altar (idempotent)
$execute unless data storage last_ember:altars a.$(aid) run data modify storage last_ember:altars a.$(aid) set value {id:"$(aid)",ch:$(ch),dim:"$(dim)",x:$(x),y:$(y),z:$(z),n:$(n),built:0b,done:0b,ev:-1}
$execute unless score #fill_$(aid) le.alt matches 0.. run scoreboard players set #fill_$(aid) le.alt 0
$data modify storage last_ember:altars a.$(aid) merge value {ch:$(ch),dim:"$(dim)",x:$(x),y:$(y),z:$(z),n:$(n)}
