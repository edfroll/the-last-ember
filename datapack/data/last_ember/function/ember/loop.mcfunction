# every tick. The Ember never exists as an item on the ground (Q, full inventory, death drops are T-006).
execute as @e[type=minecraft:item] if items entity @s contents *[minecraft:custom_data~{le_ember:1b}] run kill @s
# the carrier no longer has it (thrown, put into a chest / frame / stand / hopper / mob): it returns, stale copies become invalid
execute as @a[tag=le.carrier] run function last_ember:ember/one_carrier
execute as @a[tag=le.carrier] unless function last_ember:ember/has at @s run function last_ember:ember/lost
# every 10 ticks: invalid copies are removed from players; nobody but the carrier keeps a valid one
scoreboard players add #et le.e 1
execute if score #et le.e matches 10.. run function last_ember:ember/audit
schedule function last_ember:ember/loop 1t replace
