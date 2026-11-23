# T-032: a button of Toivo's windows (trigger le.sptrig: 1 «Что ты видел?», 2 «Иди домой»): only within 6 of him; the window goes to
# the one who pressed
scoreboard players operation #k le.sp = @s le.sptrig
scoreboard players set @s le.sptrig 0
scoreboard players enable @s le.sptrig
function last_ember:spiders/gen/near_toivo
execute unless score #ok le.sp matches 1 run return 0
execute if score #k le.sp matches 1 run scoreboard players set @s le.spwin 2
execute if score #k le.sp matches 1 run return run dialog show @s last_ember:spiders/toivo_seen
execute if score #k le.sp matches 2 run scoreboard players set @s le.spwin 0
