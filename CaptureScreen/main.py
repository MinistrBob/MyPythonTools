import cv2
import numpy as np
import pyautogui
import keyboard  # Импортируем библиотеку keyboard


print("Задаем кодек и создаем объект VideoWriter")
# Задаем кодек и создаем объект VideoWriter
codec = cv2.VideoWriter_fourcc(*'mp4v')  # Измените кодек на 'mp4v'
out = cv2.VideoWriter('screen_capture.mp4', codec, 20.0, (pyautogui.size()))

print("Запуск программы")
while True:
    # Сделать снимок экрана
    img = pyautogui.screenshot()
    # Преобразовать изображение в массив numpy
    frame = np.array(img)
    # Преобразовать цвета из BGR в RGB
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # Записать кадр в файл
    out.write(frame)

    # Проверка нажатия клавиши 'q' с использованием keyboard
    if keyboard.is_pressed('q'):
        print("Клавиша 'q' нажата, завершение записи...")
        break

# Освободить объект VideoWriter
out.release()
# Закрыть все окна OpenCV
cv2.destroyAllWindows()
