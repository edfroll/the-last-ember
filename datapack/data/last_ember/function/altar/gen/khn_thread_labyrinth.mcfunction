# generated: a new holder of the key thread_labyrinth: his UUID is stored (reading the player's data only when the holder changes)
tag @a[tag=le.kh_thread_labyrinth] remove le.kh_thread_labyrinth
tag @s add le.kh_thread_labyrinth
data modify storage last_ember:keys k.thread_labyrinth.h set from entity @s UUID
