# ДЗ по конфигурационному управлению
## Задание 1

### Описание
Эмулятор для языка оболочки ОС, похож на сеанс bash в Linux. Имеет свой GUI. Рядом с программой находится файл config.json, в котором указаны путь до стартового скрипта и .tar архив с файловой системой.

### Функции
- Выполнение команд: ls, cd, exit, uname, cat, rmdir
    - ls - вывод список файлов и каталогов в текущем каталоге
    - cd DIR - изменяет текущий каталог на указанный
    - exit - завершает работу программы
    - uname - выводит имя операционной системы
    - rmdir DIR - удаляет указанный каталог  
- Исполнение стартового скрипта при запуске эмулятора.
- exit сохраняет файловую систему обратно в архив.

### Запуск проекта

```bash
git clone https://github.com/Fisteshak/config_managment
cd config_managment
python task1/main.py
```
### Пример использования
![](/images/image1-2.png)

### Тестирование
![](/images/tests1.png)

## Задание 2

### Описание
Визуализатор графа зависимостей для пакетов python, включая транзитивные зависимости. Граф генерируется в представлении mermaid и отображается в графическом виде. 

### Параметры
Параметры задаются следующими ключами командной строки:
- --output - путь к файлу-результату
- --package - имя пакета для анализа
- --max-depth - максимальная глубина анализа
- --vis-path - путь к программе для визуализации графов. Рекомендуется использовать vis.py, входящий в состав репозитория.
- --repository - путь к репозиторию

### Запуск проекта

```bash
git clone https://github.com/Fisteshak/config_managment
cd config_managment/task2
python ./main.py --output OUTPUT --package PACKAGE [--max-depth MAX_DEPTH] [--repository REPOSITORY] [--vis-path VIS_PATH]
```
### Пример использования
![](/images/image2-1.png)

![](/images/image2-3.png)

![](/images/image2-2.png)

### Тестирование
![](/images/tests2.png)
