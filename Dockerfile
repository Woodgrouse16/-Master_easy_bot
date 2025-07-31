# Используем официальный образ Python 3.11 slim (легковесный)
FROM python:3.11-slim

# Устанавливаем системные зависимости для сборки aiohttp и других пакетов
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Создаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файл с зависимостями в контейнер
COPY requirements.txt .

# Устанавливаем Python-библиотеки из requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Копируем весь проект в контейнер
COPY . .

# Команда запуска бота
CMD ["python", "main.py"]
