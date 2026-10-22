# macro pid aid key filled
$execute if data storage last_ember:altars a.$(aid){done:1b} run return run title @a[tag=le.clicker] actionbar {"text":"Алтарь завершён. Ключи остаются здесь навсегда.","color":"gray"}
$execute unless data storage last_ember:altars a.$(aid){ev:-1} run return run title @a[tag=le.clicker] actionbar {"text":"Алтарь пробуждается…","color":"gray"}
$execute if data storage last_ember:altars p.p$(pid){filled:1b} run return run function last_ember:altar/take_do with storage last_ember:altar ped
$data modify storage last_ember:altar ped.gen set from storage last_ember:keys k.$(key).gen
function last_ember:altar/place_do with storage last_ember:altar ped
