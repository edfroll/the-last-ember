execute as @a[scores={le.deaths=1..}] run function last_ember:death/died
schedule function last_ember:death/loop 1t replace
