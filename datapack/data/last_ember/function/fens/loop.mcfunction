# T-026: every 5 ticks: the give buttons; while somebody is in the fens (or within 32): the heads of the pools, the Master of the Causeway;
# every second the rest (fens/second)
schedule function last_ember:fens/loop 5t replace
execute store result score #gt le.fn run time query gametime
scoreboard players add #t le.fn 5
execute as @a[scores={le.fgive=1..}] at @s run function last_ember:fens/give_trig
execute in minecraft:overworld run function last_ember:fens/gen/near
execute if score #near le.fn matches 1.. in minecraft:overworld run function last_ember:fens/gen/pools
execute if score #near le.fn matches 1.. in minecraft:overworld run function last_ember:fens/gen/master_check
execute unless score #near le.fn matches 1.. if score #ms le.fn matches 1 in minecraft:overworld run function last_ember:fens/gen/master_check
scoreboard players operation #t20 le.fn = #t le.fn
scoreboard players operation #t20 le.fn %= #20 le.fn
execute if score #t20 le.fn matches 0 in minecraft:overworld run function last_ember:fens/second
