# generated: tile 87 of 'chapter1' (faded when #fade_chapter1 le.bio = 1, else back)
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 492 40 24 523 71 40 last_ember:castle_dream_faded replace last_ember:castle_dream
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 492 72 24 523 103 40 last_ember:castle_dream_faded replace last_ember:castle_dream
execute if score #fade_chapter1 le.bio matches 1 run fillbiome 492 104 24 523 120 40 last_ember:castle_dream_faded replace last_ember:castle_dream
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 492 40 24 523 71 40 last_ember:castle_dream replace last_ember:castle_dream_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 492 72 24 523 103 40 last_ember:castle_dream replace last_ember:castle_dream_faded
execute unless score #fade_chapter1 le.bio matches 1 run fillbiome 492 104 24 523 120 40 last_ember:castle_dream replace last_ember:castle_dream_faded
scoreboard players operation #bt_chapter1_87 le.bio = #fade_chapter1 le.bio
