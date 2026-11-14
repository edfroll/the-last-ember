# generated: tile 57 of 'chapter1' (faded when #fade_chapter1 le.bio = 1, else back)
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 252 -64 502 276 -33 526 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 252 -32 502 276 -1 526 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 252 0 502 276 31 526 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 252 32 502 276 63 526 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 252 64 502 276 95 526 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 252 96 502 276 127 526 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 252 128 502 276 159 526 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 252 160 502 276 191 526 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 252 192 502 276 223 526 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 252 224 502 276 255 526 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 252 256 502 276 287 526 last_ember:barrows_faded replace last_ember:barrows
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 252 288 502 276 319 526 last_ember:barrows_faded replace last_ember:barrows
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 252 -64 502 276 -33 526 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 252 -32 502 276 -1 526 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 252 0 502 276 31 526 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 252 32 502 276 63 526 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 252 64 502 276 95 526 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 252 96 502 276 127 526 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 252 128 502 276 159 526 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 252 160 502 276 191 526 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 252 192 502 276 223 526 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 252 224 502 276 255 526 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 252 256 502 276 287 526 last_ember:barrows replace last_ember:barrows_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 252 288 502 276 319 526 last_ember:barrows replace last_ember:barrows_faded
scoreboard players operation #bt_chapter1_57 le.bio = #fade_chapter1 le.bio
