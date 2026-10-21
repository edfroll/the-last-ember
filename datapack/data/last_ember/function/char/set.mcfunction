# TEST/ADMIN: as a player: function last_ember:char/set {race:1..5,class:1..4,tier:0..6}; the kit is given once (tag le.kit)
$scoreboard players set #id le.e $(race)
function last_ember:char/gen/race_choose
$scoreboard players set @s le.tier $(tier)
$scoreboard players set #id le.e $(class)
scoreboard players add #id le.e 10
function last_ember:char/gen/class_choose
