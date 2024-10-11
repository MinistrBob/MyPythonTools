import os
import speech_recognition as sr
from pydub import AudioSegment
from multiprocessing import Pool, cpu_count

# Функция для транскрибирования одного MP3 файла и сохранения результата в текстовый файл
def transcribe_mp3_to_text(mp3_file, chunk_length=60):
    print(f"Конвертируем {mp3_file} в WAV формат...")

    # Конвертируем MP3 в WAV
    audio = AudioSegment.from_mp3(mp3_file)
    wav_file = mp3_file.replace(".mp3", ".wav")
    audio.export(wav_file, format="wav")
    print(f"Файл {mp3_file} успешно конвертирован в {wav_file}.")

    recognizer = sr.Recognizer()
    audio = AudioSegment.from_wav(wav_file)

    # Получаем длительность аудиофайла
    duration_in_seconds = len(audio) // 1000
    print(f"Длительность аудио: {duration_in_seconds} секунд.")

    transcript = ""

    # Проходим по файлу, разбивая его на части
    for i in range(0, duration_in_seconds, chunk_length):
        print(f"Обрабатываем фрагмент {i // chunk_length + 1}: с {i} по {i + chunk_length} секунд.")

        # Извлекаем фрагмент
        chunk = audio[i*1000:(i+chunk_length)*1000]
        chunk_wav_file = f"chunk_{i//chunk_length}.wav"
        chunk.export(chunk_wav_file, format="wav")
        print(f"Фрагмент сохранен как {chunk_wav_file}.")

        # Транскрибируем текущий фрагмент
        with sr.AudioFile(chunk_wav_file) as source:
            audio_data = recognizer.record(source)
            try:
                print(f"Транскрибируем фрагмент {i // chunk_length + 1}...")
                text = recognizer.recognize_google(audio_data, language="ru-RU")
                print(f"Текст фрагмента {i // chunk_length + 1}: {text}")
                transcript += text + " "
            except sr.UnknownValueError:
                print(f"Не удалось распознать фрагмент {i // chunk_length + 1}. Добавляем '[Неразборчиво]'.")
                transcript += "[Неразборчиво] "
            except sr.RequestError as e:
                print(f"Ошибка запроса к API на фрагменте {i // chunk_length + 1}: {e}")
                return

    # Сохраняем транскрибированный текст в текстовый файл
    text_file = mp3_file.replace(".mp3", ".txt")
    with open(text_file, "w", encoding="utf-8") as f:
        f.write(transcript)

    print(f"Транскрипция завершена для {mp3_file}. Результат сохранен в {text_file}.")

# Функция для обработки всех файлов в папке и подпапках
def process_folder(folder_path):
    mp3_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".mp3"):
                mp3_files.append(os.path.join(root, file))

    return mp3_files

# Функция для параллельной обработки с помощью multiprocessing
def transcribe_files_in_parallel(folder_path):
    mp3_files = process_folder(folder_path)
    print(f"Найдено {len(mp3_files)} MP3 файлов для обработки.")

    # Определяем количество потоков для параллельной обработки
    num_cores = cpu_count()
    print(f"Используем {num_cores} ядер для параллельной обработки.")

    # Создаем пул потоков
    with Pool(num_cores) as pool:
        pool.map(transcribe_mp3_to_text, mp3_files)

# Оборачиваем основной код в конструкцию if __name__ == "__main__":
if __name__ == "__main__":
    folder_path = r"d:\YandexDisk\!SAVE"
    print("Начинаем параллельную транскрипцию файлов...")
    transcribe_files_in_parallel(folder_path)
