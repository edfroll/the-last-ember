# as a knight: attack speed +20% (tier 0) -> +40% (tier 6), linear
scoreboard players operation #v le.e = @s le.tier
scoreboard players operation #v le.e *= #200 le.e
scoreboard players operation #v le.e /= #6 le.e
scoreboard players add #v le.e 200
execute store result storage last_ember:char tmp.v double 0.001 run scoreboard players get #v le.e
function last_ember:char/knight_tier_m with storage last_ember:char tmp
