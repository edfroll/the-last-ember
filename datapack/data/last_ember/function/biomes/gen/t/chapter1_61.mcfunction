# generated: tile 61 of 'chapter1' (faded when #fade_chapter1 le.bio = 1, else back)
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 256 -64 -24 287 -33 7 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 256 -32 -24 287 -1 7 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 256 0 -24 287 31 7 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 256 32 -24 287 63 7 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 256 64 -24 287 95 7 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 256 96 -24 287 127 7 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 256 128 -24 287 159 7 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 256 160 -24 287 191 7 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 256 192 -24 287 223 7 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 256 224 -24 287 255 7 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 256 256 -24 287 287 7 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 256 288 -24 287 319 7 last_ember:blood_vale replace last_ember:weeping_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 256 -64 -24 287 -33 7 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 256 -32 -24 287 -1 7 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 256 0 -24 287 31 7 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 256 32 -24 287 63 7 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 256 64 -24 287 95 7 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 256 96 -24 287 127 7 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 256 128 -24 287 159 7 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 256 160 -24 287 191 7 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 256 192 -24 287 223 7 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 256 224 -24 287 255 7 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 256 256 -24 287 287 7 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 256 288 -24 287 319 7 last_ember:weeping_vale replace last_ember:blood_vale
scoreboard players operation #bt_chapter1_61 le.bio = #fade_chapter1 le.bio
