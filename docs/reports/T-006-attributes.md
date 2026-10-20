# T-006, шаг 1 · Атрибуты окружения 26.3: биом или измерение

ДЛЯ ШТАБА · 21.10.2026 · короткий отчёт до остальной работы по T-006

## Как проверял
Список атрибутов я взял из реестра игры (`minecraft:environment_attribute`), их 51. Для каждого сделал тестовый биом в датапаке с одним этим атрибутом и запустил сервер. Игра при загрузке сама отказывает тем атрибутам, которые нельзя задавать по месту: «cannot be positional».

Два атрибута проверил вживую клиентом на залитом участке:
- **туман:** `fog_start/end_distance` и `fog_color` в биоме дают красный туман на 18 блоков (кадр `docs/reports/shots/T-006/T006_attrtest_fog.png`);
- **кровать:** `bed_rule` с `can_sleep: never` в биоме не даёт уснуть.

## Результат
**Только на измерение (в биоме нельзя, игра не загрузит), 2 атрибута:**
- `gameplay/fast_lava`;
- `gameplay/sky_light_level`.

**Можно в биоме, остальные 49**, в том числе:
- `visual/fog_start_distance`, `fog_end_distance`, `fog_color`, `sky_color`, `water_fog_*`, `sky_fog_end_distance`, `cloud_fog_end_distance`, `cloud_color`, `cloud_height`;
- `visual/block_light_tint`, `ambient_light_color`, `sky_light_color`, `sky_light_factor`, `night_vision_color`, `sunrise_sunset_color`;
- `visual/ambient_particles`, `default_dripstone_particle`;
- `visual/sun_angle`, `moon_angle`, `star_angle`, `star_brightness`, `moon_phase`: загружаются в биоме, но вживую я их не проверял;
- `audio/background_music`, `music_volume`, `ambient_sounds`, `firefly_bush_sounds`;
- `gameplay/natural_mob_spawns` (спавн мобов теперь атрибут), `monsters_burn`, `bed_rule`, `straw_bed_rule`, `respawn_anchor_works`, `increased_fire_burnout`, `snow_golem_melts`, `water_evaporates`, `creaking_active`, `eyeblossom_open`, `can_pillager_patrol_spawn`, `can_start_raid`, `surface_slime_spawn_chance`, `creature_world_gen_spawn_probability`, `piglins_zombify`, `nether_portal_spawns_piglin`, `bees_stay_in_hive`, `villager_activity`, `baby_villager_activity`, `cat_waking_up_gift_chance`, `turtle_egg_hatch_chance`.

**Остались свойствами самого биома** (блок `effects` и корень JSON, это не атрибуты): `grass_color`, `foliage_color`, `dry_foliage_color`, `water_color`, `temperature`, `downfall`, `has_precipitation`.

## Что из этого важно для реестра
- Туман, свет, частицы, музыка, звуки, правила кроватей, горение нежити и спавн можно задавать каждому своему биому отдельно, как и задумано в реестре.
- В биоме атрибут работает поверх измерения. Наш механизм костров и так переустанавливает точку возрождения, поэтому `bed_rule` в биомах нужен только для сна (например, запретить сон в Курганах).
- Атрибут, который у измерения задан расписанием по времени суток (цвет неба и т. п.), в биоме можно задать модификатором поверх измерения (`modifier: overlay` и др., как у ванильного бледного сада). Если нужен ночной цвет отдельно от дневного, проверю, как модификаторы сочетаются с суточным расписанием.
- **Ограничения `fillbiome`:** не больше 32 768 блоков за команду, заливка идёт ячейками 4×4×4. Клиент видит новый биом только когда чанк пересылается: в проверке цвет поменялся после ухода игрока и возвращения. Решение для «угасших» версий без перезахода — в пункте 4 задачи.
