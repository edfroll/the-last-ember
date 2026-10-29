# a clickable line of a choice (trigger le.choice = choice*10 + option)
scoreboard players operation #v le.ct = @s le.choice
scoreboard players set @s le.choice 0
function last_ember:contract/gen/choice
