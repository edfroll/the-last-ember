# generated: tile 71 of 'chapter1' (faded when #fade_chapter1 le.bio = 1, else back)
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 288 -64 40 319 -33 71 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 288 -32 40 319 -1 71 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 288 0 40 319 31 71 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 288 32 40 319 63 71 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 288 64 40 319 95 71 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 288 96 40 319 127 71 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 288 128 40 319 159 71 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 288 160 40 319 191 71 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 288 192 40 319 223 71 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 288 224 40 319 255 71 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 288 256 40 319 287 71 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 288 288 40 319 319 71 last_ember:blood_vale replace last_ember:weeping_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 288 -64 40 319 -33 71 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 288 -32 40 319 -1 71 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 288 0 40 319 31 71 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 288 32 40 319 63 71 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 288 64 40 319 95 71 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 288 96 40 319 127 71 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 288 128 40 319 159 71 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 288 160 40 319 191 71 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 288 192 40 319 223 71 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 288 224 40 319 255 71 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 288 256 40 319 287 71 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 288 288 40 319 319 71 last_ember:weeping_vale replace last_ember:blood_vale
scoreboard players operation #bt_chapter1_71 le.bio = #fade_chapter1 le.bio
