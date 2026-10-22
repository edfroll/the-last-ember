# no one is charging any more: the weather as it was before
scoreboard players set #wact le.e 0
execute if score #wprev le.e matches 0 run weather clear
execute if score #wprev le.e matches 1 run weather rain
