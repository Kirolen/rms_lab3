# Image Compression

Навчальний застосунок для порівняння власних реалізацій DCT (блоки 8×8) і DWT Хаара (3 рівні).

Відкриває зображення, готує сірий кадр 512×512, регулює частку збережених коефіцієнтів, показує PSNR, проводить експерименти та експортує PNG і CSV. Частка коефіцієнтів не дорівнює розміру закодованого файла.

Готовий запуск: `dist/ImageCompression.exe`.

Запуск із коду (Python 3.13):

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```
