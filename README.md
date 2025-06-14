# Telegram Gift Bot

Бот для автоматической покупки подарков в Telegram.

## Функциональность

- Пополнение баланса в звездах
- Настройка автоматической покупки подарков
- Установка лимитов цены и количества
- Настройка количества циклов покупки

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/telegram-gift-bot.git
cd telegram-gift-bot
```

2. Создайте файл `.env` и добавьте необходимые переменные окружения:
```
BOT_TOKEN=your_bot_token_here
ADMIN_IDS=123456789,987654321
DATABASE_URL=sqlite:///bot.db
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Запустите бота:
```bash
python app/bot.py
```

## Docker

Для запуска в Docker:

1. Соберите образ:
```bash
docker build -t telegram-gift-bot .
```

2. Запустите контейнер:
```bash
docker run -d --name gift-bot telegram-gift-bot
```

## Структура проекта

```
my_telegram_bot/
├── app/
│   ├── __init__.py
│   ├── config.py                # Конфигурация
│   ├── handlers/                # Хендлеры
│   ├── keyboards/              # Клавиатуры
│   ├── middlewares/            # Мидлвари
│   ├── services/               # Сервисы
│   ├── database/               # База данных
│   ├── utils/                  # Утилиты
│   └── bot.py                  # Инициализация бота
├── main.py                     # Точка входа
├── .env                        # Переменные окружения
├── requirements.txt
└── README.md
```

## Лицензия

MIT 