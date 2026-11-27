# T-034: every 5 ticks: an owner asleep wakes when a player alive comes into its lair (only with the lair loaded and a player within 64)
schedule function last_ember:treasury/loop 5t replace
function last_ember:treasury/gen/ogre/loop5
function last_ember:treasury/gen/grotto/loop5
function last_ember:treasury/gen/tower/loop5
