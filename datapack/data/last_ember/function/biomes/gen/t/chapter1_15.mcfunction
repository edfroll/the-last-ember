# generated: tile 15 of 'chapter1' (faded when #fade_chapter1 le.bio = 1, else back)
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 136 -64 -380 167 -33 -349 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 136 -32 -380 167 -1 -349 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 136 0 -380 167 31 -349 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 136 32 -380 167 63 -349 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 136 64 -380 167 95 -349 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 136 96 -380 167 127 -349 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 136 128 -380 167 159 -349 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 136 160 -380 167 191 -349 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 136 192 -380 167 223 -349 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 136 224 -380 167 255 -349 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 136 256 -380 167 287 -349 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 136 288 -380 167 319 -349 last_ember:blood_vale replace last_ember:weeping_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 136 -64 -380 167 -33 -349 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 136 -32 -380 167 -1 -349 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 136 0 -380 167 31 -349 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 136 32 -380 167 63 -349 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 136 64 -380 167 95 -349 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 136 96 -380 167 127 -349 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 136 128 -380 167 159 -349 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 136 160 -380 167 191 -349 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 136 192 -380 167 223 -349 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 136 224 -380 167 255 -349 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 136 256 -380 167 287 -349 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 136 288 -380 167 319 -349 last_ember:weeping_vale replace last_ember:blood_vale
scoreboard players operation #bt_chapter1_15 le.bio = #fade_chapter1 le.bio
