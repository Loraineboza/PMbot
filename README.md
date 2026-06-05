# FitLine PM Bot

Telegram-бот на Python + aiogram 3.x для консультаций по PM-International/FitLine: компания, продукты, бизнес-возможности, отзывы, заказ, регистрация, FAQ, рассылки, квиз, напоминания и админка.

Важно: реальный токен не хранится в коде. Если токен уже был отправлен в чат или попал в публичное место, безопаснее перевыпустить его в BotFather.

## Архитектура

```text
fitline_pm_bot/
├── app/
│   ├── config.py                  # .env-настройки, ссылки, админы
│   ├── content.py                 # все тексты сообщений, продукты, FAQ, библиотека
│   ├── database.py                # SQLite-репозиторий, схема и методы
│   ├── states.py                  # FSM-состояния
│   ├── handlers/
│   │   ├── common.py              # /start, /menu, /help, подписка, библиотека
│   │   ├── company.py             # раздел "О компании"
│   │   ├── products.py            # продукты, поиск, квиз
│   │   ├── business.py            # бизнес-возможности
│   │   ├── reviews.py             # отзывы и форма отзыва
│   │   ├── order.py               # заказ, консультация, напоминания
│   │   ├── registration.py        # регистрация и конверсия в клик
│   │   ├── faq.py                 # FAQ и обращения консультанту
│   │   ├── profile.py             # профиль-заглушка
│   │   ├── admin.py               # статистика, рассылка, модерация
│   │   └── keywords.py            # автоответы на ключевые слова
│   ├── keyboards/
│   │   ├── user.py                # inline-кнопки пользователя
│   │   └── admin.py               # inline-кнопки админки
│   ├── middlewares/
│   │   ├── analytics.py           # пользователи, события, популярные кнопки
│   │   └── throttling.py          # антиспам
│   └── services/
│       ├── messages.py            # безопасный вывод/редактирование сообщений
│       ├── recommendations.py     # логика рекомендаций
│       ├── reminders.py           # фоновые напоминания
│       └── search.py              # поиск по продуктам
├── data/                          # SQLite-файл создаётся при запуске
├── deploy/systemd/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── main.py
```

## Что реализовано

- Главное меню после `/start` с разделами из ТЗ.
- Вложенные меню "О компании": история, факты, NTC, ссылки, спортивные партнёры.
- Продукты FitLine по категориям, карточки продуктов, место под `photo_file_id`, наборы, официальный магазин.
- Поиск по продукту или эффекту через текстовый ввод.
- Квиз "Какой продукт FitLine вам подходит?" с 3 вопросами и ветвлением.
- Бизнес-раздел: шаги партнёра, преимущества, компенсационный план, истории, ссылка регистрации.
- Отзывы: список опубликованных, видео-ссылки, до/после как модерируемый блок, сохранение отзывов в SQLite.
- Заказ: инструкция, ссылка магазина, 3-вопросная консультация, напоминание о повторном заказе.
- Регистрация: инструкция, стартовые варианты без обещаний и фиксации цен, отслеживание клика по регистрации.
- FAQ: 7 вопросов про продукты, доставку, противопоказания, совместимость, детей, скидки и медицинские обещания.
- Поддержка: пользователь пишет вопрос, бот сохраняет его и отправляет админам/консультанту при наличии numeric ID.
- Рассылки только по согласию пользователя.
- Админка `/admin`: статистика, рассылка подписчикам, модерация отзывов.
- Антиспам middleware и базовая валидация ввода.

## Быстрый запуск локально

Перейдите в папку проекта:

```bash
cd /Users/paul/Documents/Playground/fitline_pm_bot
```

Создайте `.env`:

```bash
cp .env.example .env
```

Откройте `.env` и заполните:

```env
BOT_TOKEN=ваш_токен_из_BotFather
ADMIN_IDS=ваш_telegram_numeric_id
CONSULTANT_USERNAME=Elfrida777
CONSULTANT_TG_ID=
```

`ADMIN_IDS` — это числовой Telegram ID, не username. Его можно узнать через бота вроде `@userinfobot`. Если консультант должен получать сообщения прямо в боте, он должен сначала открыть этого бота, а вы должны указать его numeric ID в `CONSULTANT_TG_ID`. Иначе бот даст ссылку `https://t.me/Elfrida777` и будет уведомлять админов.

Установите зависимости:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Запустите бота:

```bash
.venv/bin/python main.py
```

Чтобы увидеть бота в Telegram:

1. Откройте Telegram.
2. Найдите username бота, который вы создали в BotFather.
3. Нажмите Start или отправьте `/start`.
4. Должно появиться приветствие FitLine PM Bot и inline-меню.

## Локальная проверка

```bash
PYTHONPYCACHEPREFIX=/Users/paul/Documents/Playground/fitline_pm_bot/data/pycache .venv/bin/python -m compileall app main.py
BOT_TOKEN=123:abc CONSULTANT_TG_ID= .venv/bin/python -c "import main; print('import-ok')"
```

## Docker

```bash
cd /Users/paul/Documents/Playground/fitline_pm_bot
cp .env.example .env
# заполните .env
docker compose up -d --build
docker compose logs -f
```

SQLite хранится в `./data`, каталог проброшен в контейнер.

## systemd на VPS

Пример для Ubuntu:

```bash
sudo useradd --system --create-home --shell /usr/sbin/nologin fitlinebot
sudo mkdir -p /opt/fitline_pm_bot
sudo chown -R fitlinebot:fitlinebot /opt/fitline_pm_bot
```

Скопируйте проект в `/opt/fitline_pm_bot`, затем:

```bash
cd /opt/fitline_pm_bot
sudo -u fitlinebot python3 -m venv .venv
sudo -u fitlinebot .venv/bin/pip install -r requirements.txt
sudo -u fitlinebot cp .env.example .env
sudo -u fitlinebot nano .env
sudo cp deploy/systemd/fitline-pm-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now fitline-pm-bot
sudo journalctl -u fitline-pm-bot -f
```

## Render

Вариант 1: Docker service.

- Загрузите проект в GitHub.
- Создайте Web Service или Background Worker с Dockerfile.
- В Environment добавьте `BOT_TOKEN`, `ADMIN_IDS`, `CONSULTANT_USERNAME`, ссылки.
- Для SQLite нужен persistent disk, смонтированный в `/app/data`. Без диска база будет сбрасываться при пересоздании контейнера.

Вариант 2: лучше для продакшена — PostgreSQL. В `app/database.py` оставлен комментарий, где заменить SQLite-репозиторий на SQLAlchemy/asyncpg.

## Yandex Cloud

- Создайте VM или Container Registry + Serverless Container.
- Для polling проще VM: Docker Compose или systemd.
- Для Serverless Container лучше перейти на webhook-режим aiogram и внешний HTTPS endpoint.
- Секреты храните в переменных окружения/секретах, не в репозитории.

## Инструкция администратора

Откройте `/admin`. Команда сработает только если ваш numeric Telegram ID указан в `.env`:

```env
ADMIN_IDS=123456789
```

В админке:

- `📊 Статистика` — пользователи, подписчики, отзывы, обращения, клики по регистрации, завершённые квизы, популярные callback-кнопки.
- `📣 Рассылка` — отправляет текст только пользователям, которые нажали `Подписаться`.
- `📝 Модерация отзывов` — показывает первый отзыв в очереди, можно одобрить или отклонить.

Отзывы публикуются только после модерации. Не публикуйте тексты с обещаниями лечения, диагнозами, гарантированными результатами или агрессивной рекламой БАДов.

## Как добавить фото продуктов

1. Отправьте фото нужному Telegram-боту.
2. Получите `file_id` через временный handler или через Telegram Bot API `getUpdates`.
3. Вставьте значение в `app/content.py`:

```python
"photo_file_id": "AgACAgIAAxkBAA...",
```

Если `photo_file_id = None`, бот отправляет текстовую карточку без фото.

## Будущие интеграции

- CRM: добавить таблицу связки `telegram_user_id -> pm_customer_id`.
- Оплата: отдельный payment provider handler, не смешивать с консультационным сценарием.
- Google Sheets: заменить `add_review`/`add_support_request` на сервис синхронизации.
- PostgreSQL: вынести SQL в миграции Alembic или перейти на SQLAlchemy async.

## Официальные источники контента

- PM-International: https://www.pm-international.com/ru/
- О продуктах: https://www.pm-international.com/ru/ru-ru/about-our-products
- FitLine Shop: https://www.fitline.com/
- Регистрация PM: https://www.pmebusiness.com/
- PMTV материалы: https://tv.pm-international.com/products-range и https://tv.pm-international.com/fitline-innovation

