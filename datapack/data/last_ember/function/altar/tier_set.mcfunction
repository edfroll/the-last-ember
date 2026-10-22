# as a player whose tier differs from #t
scoreboard players operation #old le.alt = @s le.tier
execute store result storage last_ember:altar t.tier int 1 run scoreboard players get #t le.alt
function last_ember:char/set_tier with storage last_ember:altar t
execute if score #t le.alt > #old le.alt run function last_ember:altar/grow_msg
