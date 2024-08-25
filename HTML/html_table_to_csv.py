import csv
import os
from bs4 import BeautifulSoup


def html_file_to_csv(html_file_path, csv_file_path):
    with open(html_file_path, 'r', encoding='utf-8') as html_file:
        html_content = html_file.read()

    soup = BeautifulSoup(html_content, 'lxml')
    print("Ищем таблицу ...")
    table = soup.find('table')

    if not table:
        raise ValueError("No table found in the HTML content")

    print("Ищем все строки таблицы ...")
    rows = table.find_all('tr')
    i = 0
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        print("Обрабатываем строки ...")
        for row in rows:
            i += 1
            columns = row.find_all(['td', 'th'])
            writer.writerow([col.get_text(strip=True) for col in columns])
            if i % 1000 == 0:
                print(f'Обработано {i} строк.')


if __name__ == '__main__':
    # Путь к HTML файлу
    html_file_path = r'c:\!SAVE\Контакты битрикс 06.12.2020.html'
    # Путь к CSV файлу
    csv_file_path = os.path.splitext(html_file_path)[0] + '.csv'
    # csv_file_path = 'output.csv'
    # Конвертация HTML таблицы в CSV
    html_file_to_csv(html_file_path, csv_file_path)
    print(f'CSV file "{csv_file_path}" created successfully.')
