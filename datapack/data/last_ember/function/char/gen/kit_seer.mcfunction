# as a player: a random staff of five (no Wrath of the Dead Sky), a dagger, the book
execute store result score #rnd le.e run random value 1..5
execute if score #rnd le.e matches 1 run function last_ember:char/gen/staff_1
execute if score #rnd le.e matches 2 run function last_ember:char/gen/staff_2
execute if score #rnd le.e matches 3 run function last_ember:char/gen/staff_3
execute if score #rnd le.e matches 4 run function last_ember:char/gen/staff_4
execute if score #rnd le.e matches 5 run function last_ember:char/gen/staff_5
give @s minecraft:stone_sword[minecraft:custom_name={"text":"Кинжал ворожея","color":"gray","italic":false},minecraft:custom_data={le_keep:1b},minecraft:lore=[{"text":"Короткий клинок: бьёт быстро и слабо.","color":"gray","italic":false}],minecraft:attribute_modifiers=[{type:"minecraft:attack_damage",id:"last_ember:dagger_damage",amount:2,operation:"add_value",slot:"mainhand"},{type:"minecraft:attack_speed",id:"last_ember:dagger_speed",amount:-2,operation:"add_value",slot:"mainhand"}]] 1
give @s minecraft:written_book[minecraft:custom_data={le_keep:1b,le_book:1b},minecraft:written_book_content={title:"Книга ворожея",author:"Несущие",pages:["ПКМ — заклинание посоха.\nShift + ПКМ — сменить заклинание.\nУ каждого заклинания свой откат.\nПосохи бывают разные: ищи их в сокровищницах.","Пепельный Покров есть на любом посохе: жёлтые сердца тебе и тем, кто рядом."]}] 1
