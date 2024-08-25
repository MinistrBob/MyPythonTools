
import os
import asyncio
import aiohttp
import traceback
from aiohttp import ClientSession, ClientTimeout
from bs4 import BeautifulSoup
import sqlite3
from urllib.parse import urlparse, urljoin, unquote
from urllib.parse import urlparse, urljoin, unquote

# Устанавливаем соединение с базой данных SQLite
conn = sqlite3.connect('images.db')
cursor = conn.cursor()

# Создаем таблицу для хранения данных, если она не существует
cursor.execute('''
    CREATE TABLE IF NOT EXISTS images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        page_url TEXT,
        image_url TEXT,
        file_path TEXT
    )
''')

# Асинхронная функция для загрузки изображения
async def download_image(session: ClientSession, img_url, folder_path, page_url):
    try:
        async with session.get(img_url) as response:
            if response.status == 200:
                img_data = await response.read()
                file_name = os.path.basename(urlparse(img_url).path)
                file_path = os.path.join(folder_path, file_name)

                # Сохраняем изображение в файл
                with open(file_path, 'wb') as img_file:
                    img_file.write(img_data)

                # Сохраняем информацию в базу данных
                cursor.execute('''
                    INSERT INTO images (page_url, image_url, file_path)
                    VALUES (?, ?, ?)
                ''', (page_url, img_url, file_path))
                conn.commit()

    except Exception as e:
        print(f"Не удалось загрузить {img_url}: {e}")

# Асинхронная функция для загрузки страницы и парсинга изображений
async def download_images(page_url, base_folder, session):
    try:
        async with session.get(page_url) as response:
            content_type = response.headers.get('Content-Type', '').lower()

            if 'text/html' in content_type:
                soup = BeautifulSoup(await response.text(), 'html.parser')

                # Определяем папку для сохранения изображений
                parsed_url = urlparse(page_url)
                path = unquote(parsed_url.path.strip('/'))  # Декодируем путь
                folder_path = os.path.join(base_folder, path)
                os.makedirs(folder_path, exist_ok=True)

                # Находим все изображения на странице
                tasks = []  # Инициализируем список задач
                for img in soup.find_all('img'):
                    img_url = img.get('src')
                    if not img_url:
                        continue

                    # Приводим ссылку к полному URL, если она относительная
                    img_url = urljoin(page_url, img_url)

                    # Проверяем формат изображения
                    if any(img_url.endswith(ext) for ext in ['jpg', 'jpeg', 'png', 'webp']):
                        tasks.append(download_image(session, img_url, folder_path, page_url))

                # Запускаем все задачи параллельно
                await asyncio.gather(*tasks)
            else:
                print(f"Некорректный тип содержимого для {page_url}: {content_type}")

    except Exception as e:
        print(f"Ошибка при обработке {page_url} | {img_url}: {e}")
        print(f"TRACE:\n{traceback.format_exc()}")
        exit(1)

# Асинхронная функция для обхода сайта (рекурсивная для получения всех ссылок)
async def crawl_site(start_url, base_folder, session, visited=None):
    if visited is None:
        visited = set()

    if start_url in visited:
        return

    visited.add(start_url)
    print(f"Обработка {start_url}")

    await download_images(start_url, base_folder, session)

    try:
        async with session.get(start_url) as response:
            content_type = response.headers.get('Content-Type', '').lower()
            if 'text/html' not in content_type:
                print(f"Пропуск {start_url} из-за некорректного типа содержимого: {content_type}")
                return

            soup = BeautifulSoup(await response.text(), 'html.parser')

            tasks = []  # Инициализируем список задач
            for link in soup.find_all('a'):
                href = link.get('href')
                if href and not href.startswith('mailto:') and not href.startswith('#'):
                    full_url = urljoin(start_url, href)
                    if urlparse(full_url).netloc == urlparse(start_url).netloc:
                        tasks.append(crawl_site(full_url, base_folder, session, visited))

            # Запускаем рекурсивный обход сайта параллельно
            await asyncio.gather(*tasks)

    except Exception as e:
        print(f"Ошибка при обходе сайта {start_url}: {e}")
        print(f"TRACE:\n{traceback.format_exc()}")
        exit(1)

# Главная функция для запуска асинхронного процесса
async def main():
    start_url = 'https://givinschool.org/'
    base_folder = r'C:\IMAGES'

    timeout = ClientTimeout(total=60, connect=10, sock_read=30, sock_connect=10)  # Устанавливаем таймауты
    async with aiohttp.ClientSession(timeout=timeout) as session:
        await crawl_site(start_url, base_folder, session)

# Запуск асинхронной программы
asyncio.run(main())

# Закрываем соединение с базой данных
conn.close()
