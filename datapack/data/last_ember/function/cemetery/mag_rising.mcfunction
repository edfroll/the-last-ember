# T-027: 2 s of dust and scraping, then he stands up
scoreboard players add #mt le.cem 1
function last_ember:cemetery/gen/mag_dust
execute if score #mt le.cem matches 3.. run function last_ember:cemetery/mag_up
