# macro: urn name (rec): appends storage last_ember:dt rec to the urn, adds the owner's name to the plate, refreshes the urn
$data modify storage last_ember:ash urns.$(urn).trails append from storage last_ember:dt rec
$execute unless data storage last_ember:ash urns.$(urn).names[{n:"$(name)"}] run data modify storage last_ember:ash urns.$(urn).names append value {n:"$(name)"}
$function last_ember:urn/refresh {urn:"$(urn)"}
