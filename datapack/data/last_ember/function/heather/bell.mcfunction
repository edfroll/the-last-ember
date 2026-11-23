# T-031: midnight (the day time passed 18000, a player within 96 of the bell): the ringer strikes 3 times, 1 s apart; after the first
# stroke every dead thing of the zone freezes 10 s facing the belfry
function last_ember:heather/gen/bell_sound
function last_ember:heather/gen/freeze
schedule function last_ember:heather/bell_2 20t replace
schedule function last_ember:heather/bell_3 40t replace
scoreboard players add #rang le.hv 1
