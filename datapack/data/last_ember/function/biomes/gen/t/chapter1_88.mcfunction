# generated: tile 88 of 'chapter1' (faded when #fade_chapter1 le.bio = 1, else back)
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 524 40 -40 540 71 -9 last_ember:castle_dream_faded replace last_ember:castle_dream
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 524 72 -40 540 103 -9 last_ember:castle_dream_faded replace last_ember:castle_dream
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 524 104 -40 540 120 -9 last_ember:castle_dream_faded replace last_ember:castle_dream
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 524 40 -40 540 71 -9 last_ember:castle_dream replace last_ember:castle_dream_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 524 72 -40 540 103 -9 last_ember:castle_dream replace last_ember:castle_dream_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 524 104 -40 540 120 -9 last_ember:castle_dream replace last_ember:castle_dream_faded
scoreboard players operation #bt_chapter1_88 le.bio = #fade_chapter1 le.bio
