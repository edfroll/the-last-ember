# T-032: as a player in the place: fire, lava and campfires within 12 (y +-6) of him and inside the place go (the canopy must not burn;
# HQ T-032, 3: a fire of a player is at most 4.5 off him, lava runs 3); outside the place nothing is touched
execute store success score #ok le.sp run function last_ember:spiders/gen/fire_clamp
execute if score #ok le.sp matches 1 run function last_ember:spiders/fire_fill with storage last_ember:spiders f
