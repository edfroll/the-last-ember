# macro t = ticks: the protection is out (armour 0, blows count from every side)
tag @s add le.cweak
$scoreboard players set @s le.cwk $(t)
attribute @s minecraft:armor modifier add last_ember:ct_weak -1 add_multiplied_total
playsound minecraft:entity.zombie_villager.cure hostile @a ~ ~ ~ 1 0.6
