# generated: tile 85 of 'chapter1' (faded when #fade_chapter1 le.bio = 1, else back)
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 402 100 -58 431 131 -27 last_ember:castle_dream_faded replace last_ember:castle_dream
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 402 132 -58 431 163 -27 last_ember:castle_dream_faded replace last_ember:castle_dream
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 402 164 -58 431 180 -27 last_ember:castle_dream_faded replace last_ember:castle_dream
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 402 100 -58 431 131 -27 last_ember:castle_dream replace last_ember:castle_dream_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 402 132 -58 431 163 -27 last_ember:castle_dream replace last_ember:castle_dream_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 402 164 -58 431 180 -27 last_ember:castle_dream replace last_ember:castle_dream_faded
scoreboard players operation #bt_chapter1_85 le.bio = #fade_chapter1 le.bio
