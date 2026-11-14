# generated: tile 58 of 'chapter1' (faded when #fade_chapter1 le.bio = 1, else back)
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 256 -64 -120 287 -33 -89 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 256 -32 -120 287 -1 -89 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 256 0 -120 287 31 -89 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 256 32 -120 287 63 -89 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 256 64 -120 287 95 -89 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 256 96 -120 287 127 -89 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 256 128 -120 287 159 -89 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 256 160 -120 287 191 -89 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 256 192 -120 287 223 -89 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 256 224 -120 287 255 -89 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 256 256 -120 287 287 -89 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 256 288 -120 287 319 -89 last_ember:blood_vale replace last_ember:weeping_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 256 -64 -120 287 -33 -89 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 256 -32 -120 287 -1 -89 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 256 0 -120 287 31 -89 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 256 32 -120 287 63 -89 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 256 64 -120 287 95 -89 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 256 96 -120 287 127 -89 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 256 128 -120 287 159 -89 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 256 160 -120 287 191 -89 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 256 192 -120 287 223 -89 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 256 224 -120 287 255 -89 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 256 256 -120 287 287 -89 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 256 288 -120 287 319 -89 last_ember:weeping_vale replace last_ember:blood_vale
scoreboard players operation #bt_chapter1_58 le.bio = #fade_chapter1 le.bio
