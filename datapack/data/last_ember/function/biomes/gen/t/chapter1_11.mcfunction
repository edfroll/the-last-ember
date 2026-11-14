# generated: tile 11 of 'chapter1' (faded when #fade_chapter1 le.bio = 1, else back)
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 124 -64 406 155 -33 437 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 124 -32 406 155 -1 437 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 124 0 406 155 31 437 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 124 32 406 155 63 437 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 124 64 406 155 95 437 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 124 96 406 155 127 437 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 124 128 406 155 159 437 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 124 160 406 155 191 437 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 124 192 406 155 223 437 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 124 224 406 155 255 437 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 124 256 406 155 287 437 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 124 288 406 155 319 437 last_ember:barrows_faded replace last_ember:barrows
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 124 -64 406 155 -33 437 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 124 -32 406 155 -1 437 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 124 0 406 155 31 437 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 124 32 406 155 63 437 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 124 64 406 155 95 437 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 124 96 406 155 127 437 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 124 128 406 155 159 437 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 124 160 406 155 191 437 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 124 192 406 155 223 437 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 124 224 406 155 255 437 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 124 256 406 155 287 437 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 124 288 406 155 319 437 last_ember:barrows replace last_ember:barrows_faded
scoreboard players operation #bt_chapter1_11 le.bio = #fade_chapter1 le.bio
