# FOR EDWARD (as a player): /function last_ember:lab/voice {k:"fish",v:2} — the sounds of the giant silverfish (fish) or of the swamp womb (womb): variant 1, 2 or 3; a sample plays at once
$scoreboard players set #v_$(k) le.l $(v)
$function last_ember:lab/s/say_$(k)_$(v)
$execute at @s run function last_ember:lab/s/$(k)_swing
