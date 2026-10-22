execute if entity @a[tag=le.clicker,tag=le.hi_smith] run return 0
tellraw @a[tag=le.clicker] [{"text":"<Кузнец Хальвард> ","color":"gold"},{"text":"Железа мало. Принеси то, что сняли с чудищ, — и я найду, чем помочь."}]
tag @a[tag=le.clicker] add le.hi_smith
