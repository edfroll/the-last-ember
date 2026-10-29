# every second: place the containers of the treasuries whose chunk got loaded (each once)
function last_ember:vault/gen/pending
schedule function last_ember:vault/loop 20t replace
