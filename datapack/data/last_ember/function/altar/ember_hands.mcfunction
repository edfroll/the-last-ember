# every tick, as the carrier: Shift + F (swap hands) with the Ember in the main hand = the Call. The datapack puts everything back as it was and casts it.
execute store success score #nm le.alt if items entity @s weapon.mainhand *[minecraft:custom_data~{le_ember:1b}]
execute store success score #no le.alt if items entity @s weapon.offhand *[minecraft:custom_data~{le_ember:1b}]
execute if score @s le.emain matches 1 if score @s le.eoff matches 0 if score #nm le.alt matches 0 if score #no le.alt matches 1 if score #chapters le.alt matches 3.. if predicate last_ember:sneaking run function last_ember:altar/swap_call
execute store result score @s le.emain if items entity @s weapon.mainhand *[minecraft:custom_data~{le_ember:1b}]
execute store result score @s le.eoff if items entity @s weapon.offhand *[minecraft:custom_data~{le_ember:1b}]
