# generated: tile 89 of 'chapter1' (faded when #fade_chapter1 le.bio = 1, else back)
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 524 40 -8 540 71 23 last_ember:castle_dream_faded replace last_ember:castle_dream
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 524 72 -8 540 103 23 last_ember:castle_dream_faded replace last_ember:castle_dream
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 524 104 -8 540 120 23 last_ember:castle_dream_faded replace last_ember:castle_dream
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 524 40 -8 540 71 23 last_ember:castle_dream replace last_ember:castle_dream_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 524 72 -8 540 103 23 last_ember:castle_dream replace last_ember:castle_dream_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 524 104 -8 540 120 23 last_ember:castle_dream replace last_ember:castle_dream_faded
scoreboard players operation #bt_chapter1_89 le.bio = #fade_chapter1 le.bio
