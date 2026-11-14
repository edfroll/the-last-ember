# generated: tile 10 of 'chapter1' (faded when #fade_chapter1 le.bio = 1, else back)
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 124 -64 374 155 -33 405 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 124 -32 374 155 -1 405 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 124 0 374 155 31 405 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 124 32 374 155 63 405 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 124 64 374 155 95 405 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 124 96 374 155 127 405 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 124 128 374 155 159 405 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 124 160 374 155 191 405 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 124 192 374 155 223 405 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 124 224 374 155 255 405 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 124 256 374 155 287 405 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 124 288 374 155 319 405 last_ember:barrows_faded replace last_ember:barrows
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 124 -64 374 155 -33 405 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 124 -32 374 155 -1 405 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 124 0 374 155 31 405 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 124 32 374 155 63 405 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 124 64 374 155 95 405 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 124 96 374 155 127 405 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 124 128 374 155 159 405 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 124 160 374 155 191 405 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 124 192 374 155 223 405 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 124 224 374 155 255 405 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 124 256 374 155 287 405 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 124 288 374 155 319 405 last_ember:barrows replace last_ember:barrows_faded
scoreboard players operation #bt_chapter1_10 le.bio = #fade_chapter1 le.bio
