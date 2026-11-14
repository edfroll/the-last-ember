# generated: tile 44 of 'chapter1' (faded when #fade_chapter1 le.bio = 1, else back)
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 220 -64 502 251 -33 526 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 220 -32 502 251 -1 526 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 220 0 502 251 31 526 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 220 32 502 251 63 526 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 220 64 502 251 95 526 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 220 96 502 251 127 526 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 220 128 502 251 159 526 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 220 160 502 251 191 526 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 220 192 502 251 223 526 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 220 224 502 251 255 526 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 220 256 502 251 287 526 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 220 288 502 251 319 526 last_ember:barrows_faded replace last_ember:barrows
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 220 -64 502 251 -33 526 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 220 -32 502 251 -1 526 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 220 0 502 251 31 526 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 220 32 502 251 63 526 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 220 64 502 251 95 526 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 220 96 502 251 127 526 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 220 128 502 251 159 526 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 220 160 502 251 191 526 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 220 192 502 251 223 526 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 220 224 502 251 255 526 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 220 256 502 251 287 526 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 220 288 502 251 319 526 last_ember:barrows replace last_ember:barrows_faded
scoreboard players operation #bt_chapter1_44 le.bio = #fade_chapter1 le.bio
