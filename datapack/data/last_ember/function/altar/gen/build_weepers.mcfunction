# generated: the interactions and labels of the pedestals of weepers (as a function run in the dimension)
summon minecraft:interaction -413.5 111 -185.5 {width:1.1f,height:1.6f,response:1b,Tags:["le.ped","le.ped1"]}
execute positioned -413.5 111 -185.5 run scoreboard players set @e[type=minecraft:interaction,tag=le.ped1,distance=..1] le.pid 1
summon minecraft:text_display -413.5 112.95 -185.5 {billboard:"center",text:{"text":"Нить Лабиринта","color":"dark_gray"},background:0,see_through:0b,Tags:["le.ped_lbl","le.ped_lbl1"],brightness:{sky:6,block:6}}
summon minecraft:interaction -410.5 111 -179.5 {width:1.1f,height:1.6f,response:1b,Tags:["le.ped","le.ped2"]}
execute positioned -410.5 111 -179.5 run scoreboard players set @e[type=minecraft:interaction,tag=le.ped2,distance=..1] le.pid 2
summon minecraft:text_display -410.5 112.95 -179.5 {billboard:"center",text:{"text":"Слеза Скрипуна","color":"dark_gray"},background:0,see_through:0b,Tags:["le.ped_lbl","le.ped_lbl2"],brightness:{sky:6,block:6}}
summon minecraft:interaction -413.5 111 -173.5 {width:1.1f,height:1.6f,response:1b,Tags:["le.ped","le.ped3"]}
execute positioned -413.5 111 -173.5 run scoreboard players set @e[type=minecraft:interaction,tag=le.ped3,distance=..1] le.pid 3
summon minecraft:text_display -413.5 112.95 -173.5 {billboard:"center",text:{"text":"Перстень Спящего Короля","color":"dark_gray"},background:0,see_through:0b,Tags:["le.ped_lbl","le.ped_lbl3"],brightness:{sky:6,block:6}}
summon minecraft:interaction -419.5 111 -170.5 {width:1.1f,height:1.6f,response:1b,Tags:["le.ped","le.ped4"]}
execute positioned -419.5 111 -170.5 run scoreboard players set @e[type=minecraft:interaction,tag=le.ped4,distance=..1] le.pid 4
summon minecraft:text_display -419.5 112.95 -170.5 {billboard:"center",text:{"text":"Венец Трёх Ведьм","color":"dark_gray"},background:0,see_through:0b,Tags:["le.ped_lbl","le.ped_lbl4"],brightness:{sky:6,block:6}}
data modify storage last_ember:altars a.weepers.built set value 1b
