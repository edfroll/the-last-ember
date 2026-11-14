# generated: tile 77 of 'chapter1' (faded when #fade_chapter1 le.bio = 1, else back)
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 320 -64 -24 348 -33 7 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 320 -32 -24 348 -1 7 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 320 0 -24 348 31 7 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 320 32 -24 348 63 7 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 320 64 -24 348 95 7 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 320 96 -24 348 127 7 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 320 128 -24 348 159 7 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 320 160 -24 348 191 7 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 320 192 -24 348 223 7 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 320 224 -24 348 255 7 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 320 256 -24 348 287 7 last_ember:blood_vale replace last_ember:weeping_vale
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 320 288 -24 348 319 7 last_ember:blood_vale replace last_ember:weeping_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 320 -64 -24 348 -33 7 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 320 -32 -24 348 -1 7 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 320 0 -24 348 31 7 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 320 32 -24 348 63 7 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 320 64 -24 348 95 7 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 320 96 -24 348 127 7 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 320 128 -24 348 159 7 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 320 160 -24 348 191 7 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 320 192 -24 348 223 7 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 320 224 -24 348 255 7 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 320 256 -24 348 287 7 last_ember:weeping_vale replace last_ember:blood_vale
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 320 288 -24 348 319 7 last_ember:weeping_vale replace last_ember:blood_vale
scoreboard players operation #bt_chapter1_77 le.bio = #fade_chapter1 le.bio
