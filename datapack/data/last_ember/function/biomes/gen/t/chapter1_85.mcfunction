# generated: tile 85 of 'chapter1' (faded when #fade_chapter1 le.bio = 1, else back)
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 492 40 -40 523 71 -9 last_ember:castle_dream_faded replace last_ember:castle_dream
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 492 72 -40 523 103 -9 last_ember:castle_dream_faded replace last_ember:castle_dream
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 492 104 -40 523 120 -9 last_ember:castle_dream_faded replace last_ember:castle_dream
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 492 40 -40 523 71 -9 last_ember:castle_dream replace last_ember:castle_dream_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 492 72 -40 523 103 -9 last_ember:castle_dream replace last_ember:castle_dream_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 492 104 -40 523 120 -9 last_ember:castle_dream replace last_ember:castle_dream_faded
scoreboard players operation #bt_chapter1_85 le.bio = #fade_chapter1 le.bio
