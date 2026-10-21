# as the player; #id le.e = pad id (1..5 peoples, 11..14 classes)
execute if score #id le.e matches 1..5 run function last_ember:char/race_click
execute if score #id le.e matches 11..14 run function last_ember:char/class_click
