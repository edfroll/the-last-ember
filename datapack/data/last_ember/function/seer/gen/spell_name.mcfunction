# as a seer: storage last_ember:seer h.name = the name of the selected spell
data modify storage last_ember:seer h.name set value "Пепельный Покров"
execute unless score @s le.spsel matches 1 if items entity @s weapon.mainhand *[minecraft:custom_data~{le_staff:"blink"}] run data modify storage last_ember:seer h.name set value "Посох Мгновения"
execute unless score @s le.spsel matches 1 if items entity @s weapon.mainhand *[minecraft:custom_data~{le_staff:"frost"}] run data modify storage last_ember:seer h.name set value "Посох Хладной Длани"
execute unless score @s le.spsel matches 1 if items entity @s weapon.mainhand *[minecraft:custom_data~{le_staff:"flame"}] run data modify storage last_ember:seer h.name set value "Посох Пламенной Жатвы"
execute unless score @s le.spsel matches 1 if items entity @s weapon.mainhand *[minecraft:custom_data~{le_staff:"lift"}] run data modify storage last_ember:seer h.name set value "Посох Отринутой Тяжести"
execute unless score @s le.spsel matches 1 if items entity @s weapon.mainhand *[minecraft:custom_data~{le_staff:"banish"}] run data modify storage last_ember:seer h.name set value "Посох Изгнания"
execute unless score @s le.spsel matches 1 if items entity @s weapon.mainhand *[minecraft:custom_data~{le_staff:"wrath"}] run data modify storage last_ember:seer h.name set value "Посох «Гнев Мёртвого Неба»"
