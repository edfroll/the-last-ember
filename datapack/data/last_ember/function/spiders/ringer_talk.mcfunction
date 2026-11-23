# T-032: called by heather/talk (as the player at the ringer): Toivo saved (q >= 2) and this player not rewarded yet - the window
# «Тойво дома», the reward of an R1 contract (give/loot: no free slot - at the feet), q 3; returns 1 when it took the talk
execute store result score #q le.sp run data get storage last_ember:heather q
execute if score #q le.sp matches ..1 run return 0
execute if entity @s[tag=le.sprew] run return 0
tag @s add le.sprew
scoreboard players set @s le.hwin 8
dialog show @s last_ember:spiders/ringer_home
function last_ember:give/loot {table:"last_ember:contract/reward_r1",need:1}
data modify storage last_ember:heather q set value 3
return 1
