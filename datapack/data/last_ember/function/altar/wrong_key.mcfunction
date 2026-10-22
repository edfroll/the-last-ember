# the clicker holds something that does not belong on this pedestal (or nothing)
execute if items entity @a[tag=le.clicker,limit=1] weapon.mainhand * run title @a[tag=le.clicker] actionbar {"text":"Здесь его место не","color":"gray"}
execute unless items entity @a[tag=le.clicker,limit=1] weapon.mainhand * run title @a[tag=le.clicker] actionbar {"text":"Нужен ключ главы","color":"gray"}
playsound minecraft:block.note_block.basedrum block @a[distance=..8] ~ ~ ~ 0.7 0.6
