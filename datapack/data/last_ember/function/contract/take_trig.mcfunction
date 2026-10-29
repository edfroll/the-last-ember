# the take button of a contract window (trigger le.ctake = the number of the contract)
scoreboard players operation #t le.ct = @s le.ctake
scoreboard players set @s le.ctake 0
function last_ember:contract/gen/take
