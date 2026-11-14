# generated: tile 42 of 'chapter1' (faded when #fade_chapter1 le.bio = 1, else back)
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 220 -64 438 251 -33 469 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 220 -32 438 251 -1 469 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 220 0 438 251 31 469 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 220 32 438 251 63 469 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 220 64 438 251 95 469 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 220 96 438 251 127 469 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 220 128 438 251 159 469 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 220 160 438 251 191 469 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 220 192 438 251 223 469 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 220 224 438 251 255 469 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 220 256 438 251 287 469 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 220 288 438 251 319 469 last_ember:barrows_faded replace last_ember:barrows
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 220 -64 438 251 -33 469 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 220 -32 438 251 -1 469 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 220 0 438 251 31 469 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 220 32 438 251 63 469 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 220 64 438 251 95 469 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 220 96 438 251 127 469 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 220 128 438 251 159 469 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 220 160 438 251 191 469 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 220 192 438 251 223 469 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 220 224 438 251 255 469 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 220 256 438 251 287 469 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 220 288 438 251 319 469 last_ember:barrows replace last_ember:barrows_faded
scoreboard players operation #bt_chapter1_42 le.bio = #fade_chapter1 le.bio
