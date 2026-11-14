# generated: tile 90 of 'chapter1' (faded when #fade_chapter1 le.bio = 1, else back)
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 524 40 24 540 71 40 last_ember:castle_dream_faded replace last_ember:castle_dream
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 524 72 24 540 103 40 last_ember:castle_dream_faded replace last_ember:castle_dream
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 524 104 24 540 120 40 last_ember:castle_dream_faded replace last_ember:castle_dream
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 524 40 24 540 71 40 last_ember:castle_dream replace last_ember:castle_dream_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 524 72 24 540 103 40 last_ember:castle_dream replace last_ember:castle_dream_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 524 104 24 540 120 40 last_ember:castle_dream replace last_ember:castle_dream_faded
scoreboard players operation #bt_chapter1_90 le.bio = #fade_chapter1 le.bio
