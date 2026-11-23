# T-032: as a player near the nest: counted (and tagged le.spin) when inside its cavity
tag @s remove le.spin
function last_ember:spiders/gen/in_nest
execute if score #in le.sp matches 1 run tag @s add le.spin
execute if score #in le.sp matches 1 run scoreboard players add #innest le.sp 1
