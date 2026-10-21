# The Last Ember — правила для агента-билдера

Dark fantasy приключенческая карта для **Minecraft Java 26.3**, кооператив 2–3 игрока.
Только ваниль: датапак + ресурс-пак. Без модов, плагинов и командных блоков.

## Роли
- **Штаб** — геймдизайн, присылает задачи, решает вопросы дизайна.
- **Архитектор** — внешний вид локаций (карточки, карты высот, эскизы).
- **Edward** — владелец, тестирует игру, пересылает сообщения между сессиями.
- Edward **не читает сюжетные подробности** (хочет пройти карту вслепую). Ему — коротко и без спойлеров: что готово, что нужно от него. Подробные отчёты адресуются Штабу и начинаются со строки «ДЛЯ ШТАБА».

## Источник правды
- Рамочный документ Штаба: `docs/design/hq-instructions.md` (+ `docs/design/framework.md`, `docs/design/world-map.png`, карточки локаций в `docs/design/locations/`).
- Онлайн-копия: https://claude.ai/code/artifact/b57cab50-5d3c-464c-8478-3fae25d6592a
- Дизайн сами не меняем. Если задача противоречит документу или невозможна в ванили — стоп, вопрос Штабу.

## Жёсткие ограничения
- Ванильный 26.3. Форматы, ID блоков, компоненты, синтаксис команд брать из игры (`docs/reference/`, генератор данных), не по памяти.
- Логика только в функциях датапака (tick/load/schedule/advancements/predicates).
- Мультиплеер 2–3 игрока: всё работает на каждого игрока отдельно и при одновременных действиях.
- Производительность: лёгкий tick, проверки по тегам и с интервалами, лимиты сущностей из документа. Прорисовка 12 чанков без шейдеров.
- Ресурс-пак не перекрашивает ванильные блоки и мобов глобально (кроме разрешённого в документе).

## Версия 26.3 — факты (из `docs/reference/version.json`)
- Pack format: датапак `121`, ресурс-пак `97`. В `pack.mcmeta` используются `min_format`/`max_format` (не `pack_format`).
- Каталоги данных в единственном числе: `function/`, `tags/function/`, `advancement/`, `loot_table/`, `predicate/`.
- Java для сервера: **25** (Temurin лежит в `server/jdk25/`, системная Java 17 не подходит).

## Структура репозитория
- `datapack/` — датапак (`data/last_ember/…`, теги `load`/`tick` в `data/minecraft/tags/function/`). Пространство имён: `last_ember`, префикс скорбордов/тегов `le.`.
- `resourcepack/` — ресурс-пак (`assets/last_ember/…`).
- `tools/` — скрипты: `server.sh` (управление сервером), `rcon.py` (RCON-клиент); сюда же сид-поиск, рендер карт, тесты.
- `server/` — локальный сервер, **не в git**: jar, JDK 25, мир, `generated/` (полный вывод генератора данных: `data/` и `reports/`).
- `docs/` — `design/` (от Штаба), `reference/` (отчёты генератора 26.3: blocks, registries, commands, datapack, version), `reports/` (отчёты Штабу).

## Тест-сервер
Первый раз: принять EULA (`server/eula.txt`: `eula=true` — только с согласия Edward), затем `tools/server.sh setup` (копирует `datapack/` (rsync; симлинки в мире запрещены) в `server/world/datapacks/last_ember`, пишет `server.properties` с RCON `127.0.0.1:25575`, пароль локальный `ember-local-rcon`, offline-mode).
- Старт: `tools/server.sh start` (передний план; для агента — запускать в фоне, лог `server/logs/latest.log`).
- Синхронизация датапака без рестарта: `tools/server.sh sync` + `reload`. Команда: `tools/server.sh rcon "reload"` / `tools/server.sh rcon "function last_ember:load"`.
- Стоп: `tools/server.sh stop`.
- Пересборка данных генератора: `server/jdk25/*/Contents/Home/bin/java -DbundlerMainClass=net.minecraft.data.Main -jar server/server-26.3.jar --reports --server --output server/generated`.

## Мир без руды (шаг 2)
- Руды в мире нет: датапак переопределяет ванильный worldgen. Файлы в `datapack/data/minecraft/worldgen/` и `datapack/data/last_ember/worldgen/` **генерируются** `python3 tools/gen_no_ore.py` из `server/generated/` — руками не править, перегенерировать скриптом (список файлов в `tools/.no-ore-manifest`).
- Что выключено: все `feature/ore_*` с рудными блоками (уголь, железо, медь, золото, редстоун, алмаз, лазурит, изумруд, незер-золото, кварц, древние обломки) → `no_op`; большие жилы железа/меди (material rule `overworld/{iron,copper}_ore_vein`); `coal_ore` в окаменелостях (→ stone) и в 5 декоративных лагерях `abandoned_camp` (процессор `last_ember:strip_ores`).
- Обычные камни (гранит, диорит, андезит, туф, гравий, глина) и заражённый камень оставлены.
- Не затронуто: руда в лутe (сырое железо/алмазы в сундуках, трейды) — это предметы, не генерация; решает дизайн.
- **ЖЁСТКОЕ ПРАВИЛО:** датапак кладётся в `world/datapacks/` **до создания боевого мира** (`tools/server.sh sync` до первого старта). Worldgen-оверрайды (руды, структуры) действуют только на новые чанки; созданные без пака чанки уже содержат ванильные руды и структуры.
- **T-001 (лут и структуры):** `python3 tools/gen_t001.py` — из ванильных таблиц лута (chests/, archaeology/, pots/, entities/, hero_of_the_village/cleric_gift) вычищены сырые руды, слитки, самородки, алмазы, изумруды, лазурит, редстоун и их блоки, у зомби/хаска/утопленника/зомби-жителя ещё морковь и картофель; у всех структур Верхнего мира и Незера `structures: []` в `structure_set` (End не тронут). Файлы генерируются (манифест `tools/.t001-manifest`), руками не править. Не тронуты: `blocks/*` (redstone_wire роняет пыль), `piglin_bartering` (экономика).
- **T-001b:** из лута убрано и снаряжение (железо/золото/алмаз/кольчуга/медь/незерит: инструменты, броня, копья, броня для лошадей и наутилусов) во всех таблицах кроме `blocks/` и бартера, включая вложенные (`equipment/trial_chamber*`); `monster_room` (подземелья со спавнерами) выключены, `end_city` выключен, `gamerule spawn_wandering_traders false` ставит `last_ember:load`. Мобы: `last_ember:mob_eq/scan` раз в 10 тиков находит новых мобов из тега `#last_ember:geared` (без тега `le.eq_done`), `mob_eq/fix` обнуляет `drop_chances` у слотов с предметом из `#last_ember:metal_gear` (тег генерируется). Наши элитки с тегом `le.elite` пропускаются: снаряжаем и ставим дроп сами.
- Тесты: `tools/scan_blocks.py <world> overworld|nether [regex|structures]`, `tools/test_loot.py [rolls]` (прокрутка таблиц через RCON; `tools/test_mobgear.py [N]` (убийства мобов игроком Cam через `damage ... by Cam`, нужен клиент в игре, ночь, сложность hard; контроль = убийство до прогона `mob_eq`; для контроля `datapack disable "file/last_ember"` возвращает ванильный лут).
- Проверка: `tools/scan_blocks.py <world> overworld|nether [regex]` читает .mca и считает палитры секций (26.x: палитра = строка | `{"id",..}` | `{"": имя}`).

## Перебор сидов (шаг 3)
- `tools/seedmap.sh <outDir> <size> <stride> <seed...>` — без сервера и чанков считает ванильный шум рельефа и биомов (Java-код `tools/seedmap/SeedMap.java` на серверном jar 26.3). Пример: `tools/seedmap.sh docs/reports/seeds 3200 8 1 42 2026` → на сид `seed_N_height.png` (рельеф с тенями, вода, сетка 400/800, красный крест = 0,0), `seed_N_biomes.png`, `seed_N_grid.json` (сетка для скоринга; в git не кладём). ~10 с на сид при шаге 8 (картинка 800×800 для 3200 блоков).
- Точность: биомы совпали с реальным миром в 97/100 точек (остальное — границы), высота верхнего блока — в 99/100 (расхождения — деревья/снег). Высоты в JSON: Y верхнего блока; `height_surface` включает воду, `height_floor` — дно/твёрдое. Использует ванильные шумы: наши оверрайды worldgen (руды/структуры) рельеф и биомы не меняют.
- Реальная генерация через сервер слишком медленна для перебора (~15 чанков/с → ~45 мин на 3200×3200).

## Автоскриншоты из игры (шаг 4)
- Реальный клиент 26.3 (файлы из лаунчера Edward'а в `~/Library/Application Support/minecraft`, запуск нашим `tools/client_launch.py` из отдельной папки `server/client/`, настройки Edward'а не трогаем) + dev-агент `tools/shotagent/ShotAgent.java` (`tools/build_shotagent.sh` → `server/shotagent.jar`, только локальный инструмент, в карту не входит). Агент по файлу-запросу делает штатный скриншот клиента (без нажатия клавиш, без прав macOS на Универсальный доступ и запись экрана), скрывает HUD, чат, закрывает меню.
- Порядок: `tools/server.sh start` → `python3 tools/client_launch.py` (ждать ~50 с, клиент заходит как `Cam`) → `python3 tools/screenshot.py shots.json [--out DIR]` (формат файла в докстринге: точки, yaw/pitch, время суток, погода; камера = spectator, `tp` по RCON). Кадры 2560×1440. Свёрнутое окно клиента (жёлтый кружок) не мешает (проверено), закрыть окно нельзя; агент сам возрождает мёртвую камеру, новичкам ставится spectator. `whitelist` на тест-сервере выключен (`white-list=false`).
- Выгрузка в 26.x: у библиотек в манифесте нет `path`, берём из `url`; в клиенте нет `Options.hideGui` (HUD: `mc.gui.hud`), нет `setScreen` у Minecraft (`mc.gui.setScreen`).

## Неразрушимые зоны (T-004)
- Зоны — `zones/zones.txt`, одна строка на зону (`id измерение box x1 y1 z1 x2 y2 z2 [флаги]` или `cyl cx cz r y1 y2`). После правки: `python3 tools/gen_zones.py` → `datapack/data/last_ember/function/zones/gen/` (генерируется, руками не править). Тестовые зоны: `python3 tools/gen_zones.py zones/test_zones.txt` (только для тест-мира, перед коммитом перегенерировать без них).
- Индекс: ячейки 64×64 на измерение, проверка игрока — только зоны его ячейки (макрос `zones/run_p`), раз в 5 тиков; каждый тик — пока кто-то планирует на элитрах, падает с высоты (`predicate last_ember:zone_fast`) или летит жемчуг. Запас 5 блоков вокруг зоны (досягаемость). Креатив/наблюдатель не трогаем; в выживание возвращаем только тех, кого перевели в приключение мы (тег `le.zadv`).
- Флаги: игрок получает теги `le.zf.<флаг>`; `no_spawn` ещё и убирает монстров (`#last_ember:monsters`, без тега `le.keep`) в пустоту раз в секунду.
- Глобально в `load`: `mob_griefing false`, `fire_spread_radius_around_player 0`, `projectiles_can_break_blocks false` (обоснование в `docs/reports/T-004-report.md`). TNT, TNT-вагонетки, кристаллы Края ближе 8 блоков к зоне обезвреживаются.
- Тесты: `tools/test_zones.py` (1 игрок, 26 проверок), `tools/test_zones_mp.py` (2 игрока: `client_launch.py --name Cam2 --dir server/client2 --mem 1500M --size 640x360`).

## Костры и Уголь (T-005)
- Костры — `bonfires/bonfires.txt` (`номер id измерение x y z main|normal регион [start]`), номер постоянный. `python3 tools/gen_bonfires.py` → `bonfire/gen/{register,build_pending,start}` + `zones/bonfires.gen.txt` (зоны r6), затем `python3 tools/gen_zones.py`. Тестовые: `gen_bonfires.py bonfires/test_bonfires.txt` (перед коммитом перегенерировать без них).
- Реестр: storage `last_ember:bonfires by.b<номер>` {state 0/1, built, rx/ry/rz точка возрождения, d измерение…}. Строится при первой загрузке тикающего чанка (`build_pending` раз в секунду). Вручную: `function last_ember:bonfire/place {…}` (поля в комментарии файла). Внешний вид — заглушка `bonfire/build_here` до карточки.
- Клики: сущности `interaction` (теги `le.hearth`/`le.stela`, номер в `le.bidx`), достижение `bonfire/click` → `bonfire/clicked`. Позиции: `positioned <целые>` уже центрирует x/z (+0.5) — сущности ставить в `~ ~ ~`.
- Возрождение: счёты игрока `le.sx/sy/sz/sd/sb`, `spawnpoint` переустанавливается раз в секунду (кровати не сбивают). Новичок → костёр `start`.
- Уголь: `trial_key` с `custom_data{le_ember:1b,gen:N}` и `item_model last_ember:ember` (анимированная текстура в ресурс-паке, `tools/make_ember_texture.py`). Ровно один действительный: при потере носителем `gen` растёт, носитель получает новый, старые копии удаляются (у игроков, в рамках/стойках/мобах рядом, в контейнере под взглядом, в эндер-сундуке). Носитель — тег `le.carrier`. Гнездо: storage `last_ember:ember socket` (-1 пусто), отображение — `item_display` с тегом `le.ember_disp`. Админ/тест: `function last_ember:ember/give_to_me`.
- Тест: `tools/test_bonfires.py` (2 клиента, клики и Q — реальный ввод через агент: строки `!use`, `!drop`, `!sneak_on/off` в `shot-request.txt`).
- **Тест-сервер: `pause-when-empty-seconds=-1`**, иначе без игроков сервер в 26.x встаёт на паузу и `schedule`-циклы не идут.

## Порядок работы
- Одна задача Штаба = ветка или серия коммитов. Каждую задачу проверять самому на сервере (RCON, тестовые функции, логи) до отчёта.
- Отчёт Штабу: что сделано; как проверено; что отличается от задачи и почему; что может проверить только живой игрок; вопросы.
- Не уточнённые вещи не выдумываем — спрашиваем.

## Биомы Р0/Р1 (T-006)
- Реестр: `biomes/registry.json` (цвета, туман, частицы, звуки, спавн, музыкальные слоты, порядок заливки `paint`, события угасания `fade`). Источник: `docs/design/biomes/registry.md`. Генерация: `python3 tools/gen_biomes.py` → `datapack/.../worldgen/biome/*.json`, `function/biomes/gen/fade_<глава>.mcfunction`, `biomes/paint.gen.json`, `resourcepack/.../sounds.json` (заглушки слотов `music.<слот>`). Руками не править.
- Заливка **офлайн** (сервер остановлен): `tools/biomepaint.sh [paint.json]` (`BiomePaint.java`) переписывает биомы 4×4×4 в существующих чанках по контурам, слои по порядку, переход = смешанная полоса ВНУТРИ контура (вероятность клетки растёт линейно от 0 на границе до 1 на `trans` блоков). Свежий мир: сгенерировать область → остановить → `biomepaint.sh` → запуск. Недогенерированные чанки пропускаются.
- Угасание главы: `function last_ember:biomes/gen/fade_chapter1` (команды `fillbiome … replace`, плитки ≤32768 блоков). Клиенты видят смену цвета сразу, без перезахода (проверено кадрами «до/после»).
- Атрибуты окружения: в биоме задаётся 49 из 51, только `fast_lava` и `sky_light_level` — на измерение (`docs/reports/T-006-attributes.md`). Музыка в биоме: `{"sound": {"sound_id": "last_ember:music.<слот>"}}` (встроенное событие, регистрировать на сервере не надо).
- Тесты: `tools/test_spawns.py [минут] [места…]` (ускоренный `tick rate`, считает мобов по биому, в котором они стоят).

## Смерть, пепельный след, Урны (T-007)
- `gamerule keep_inventory true`: ничего не падает само; `death/died` (по `deathCount`) оставляет снаряжение (броня, вторая рука), выбранный слот, Уголь и предметы с `custom_data` `le_keep`/`le_key`, остальное и опыт — в след. Предметы хранятся как есть (компоненты не теряются).
- След: storage `last_ember:ash t.t<id>` {items, lv, pts, owner, name, urn, x y z}, сущности `interaction` (тег `le.ashclick`) + `item_display` (`le.ash_disp`, модель `last_ember:ash_pile`) с `le.tid`, блок `light`. Забирает любой (ПКМ, достижение `ash/click`). У игрока `le.ash` = его след. Вторая смерть → прежний след в Урну. Лава, y < −64, «пустоты» из `death/voids.txt` → сразу в Урну. Нет места → ближайшая свободная точка ≤ 8 (`ash/gen/find_spot`), иначе Урна.
- Регионы → урны: `death/regions.txt` (Р0 и Р1 → урна `r0` Приюта, Р5 по y). Урны: `death/urns.txt` (постройка-заглушка по карточке). `python3 tools/gen_death.py [urns_file]`. Урна: storage `urns.<id>` {trails, names, pos}, ПКМ → всё тому, кто открыл, лишнее — в чашу; свечи и искры, табличка с именами (`text_display`).
- Котёл знахаря (замечание к T-005): тег класса `le.class.healer`, предмет с `custom_data le_cauldron`. Shift+ПКМ по горящему очагу — котёл над огнём; Shift+ПКМ по котлу — обратно. Тест: `function last_ember:bonfire/give_cauldron`.
- Тесты: `tools/test_death.py` (19 проверок, 2 клиента), `tools/test_cauldron.py`.

## Приют (T-008)
- Генераторы построек: `tools/build/` (`lib.py` — воксельная модель и экспорт; модули `plaza`, `gates`, `buildings`, `tower`, `hall`, `bonfire_std`, `urn`; `geo.py` — целевой рельеф и повороты). Сборка: `python3 tools/build/refuge.py` → `server/build/refuge/` (`terrain.png/json`, `refuge.txt`, куски в `pieces/`) + `function/refuge/gen/markers` (точки механик в storage `last_ember:refuge m.<имя>`) + `docs/reports/T-008-markers.txt`. Проверка состояний блоков: `python3 tools/build/validate.py <файлы>`.
- Порядок (сервер остановлен, чанки хаба сгенерированы; `server/build/refuge/heights.txt` — естественный рельеф, `tools/blockwriter.sh heights -210 -210 210 210 <файл>` на нетронутом мире): `tools/sculpt.sh apply server/build/refuge/terrain.json` → `tools/blockwriter.sh apply server/build/refuge/refuge.txt` → `tools/biomepaint.sh` → старт (костёр и Урну строит датапак). `.nbt`: `python3 tools/build/refuge.py nbt` → `structure/refuge/*.nbt`.
- `BlockWriter` (`tools/seedmap/BlockWriter.java`): офлайн-запись блоков и блочных сущностей, экспорт `.nbt`, дамп высот. **26.x: состояние блока в NBT = `{id, properties}`** (не `Name/Properties`). Соединения заборов/стен/панелей считает `tools/build/connect.py` (офлайн нет обновлений блоков).
- Варианты сквозных построек: костёр `variant=std|dol|snow|desert|ash|under` (r 3/4) → `bonfire/gen/build_<v>_r<r>`, урна `r0,r2..r6` → `urn/gen/build_<v>`; генерирует `python3 tools/build/gen_runtime.py`.
- Зоны Приюта: `refuge` (−200…200, y 50…320, no_spawn) и `refuge_well`. Биом Купели `last_ember:font_of_callings` (коробка грота).
- FPS клиента: строка `!fps` в `shot-request.txt` (ответ в `shot-done.txt`); для замера в `server/client/options.txt` `inactivityFpsLimit:"minimized"`, иначе AFK-ограничение 30.
- Ресурс-пак карты сервер выдаёт сам: `tools/server.sh sync` пакует `resourcepack/` в `server/rp/last_ember.zip` и пишет в `server.properties` URL `http://127.0.0.1:8765/last_ember.zip`, sha1 и `require-resource-pack=true`; `start` поднимает `python3 -m http.server 8765`. Новый пак — после рестарта сервера. Dev-агент сам принимает запрос пака (`PackConfirmScreen`).
- **Самопроверка ботом (Эдвард не тестирует):** `tools/build/rebuild.sh` (мир с нуля + dev-клиент), `python3 tools/build/routes.py` → `server/build/walk/*.json`, `python3 tools/walkbot.py server/build/walk/<маршрут>.json [--jump]` — реальная ходьба (клавиши через агент, `rotate` по RCON), отчёт о застреваниях/падениях с кадрами. Пути без прыжков: `graded_path` в `refuge.py` (полублоки, ≤0.5 на шаг по всей ширине), `tools/build/walkcheck.py` — BFS-проверка по блокам до выгрузки.

