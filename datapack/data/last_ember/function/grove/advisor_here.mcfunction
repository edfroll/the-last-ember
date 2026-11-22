# T-030: ADMIN (for shots): the Advisor stands here, facing the nearest player; no moves until grove/reset (or grove/advisor_free)
scoreboard players set #pin le.grv 1
scoreboard players add #agen le.grv 1
kill @e[tag=le.advent]
summon minecraft:mannequin ~ ~ ~ {Tags:["le.npc","le.keep","le.noelite","le.advisor","le.advent","le.advnew"],profile:{texture:"last_ember:entity/advisor"},CustomName:{text:"Советчик",color:"gold"},CustomNameVisible:1b,hide_description:1b,immovable:1b,Invulnerable:1b,Silent:1b,equipment:{mainhand:{id:"minecraft:stick",count:1,components:{"minecraft:item_model":"last_ember:advisor_pipe"}}}}
summon minecraft:interaction ~ ~ ~ {Tags:["le.advtalk","le.advent","le.advnew"],width:0.9f,height:2.0f,response:1b}
execute as @e[type=minecraft:mannequin,tag=le.advnew] at @s run rotate @s facing entity @p
scoreboard players operation @e[tag=le.advnew] le.agen = #agen le.grv
tag @e[tag=le.advnew] remove le.advnew
scoreboard players set #cur le.grv 3
