import csv
from io import StringIO
from schemas.schemas import GroupModel


# Функция для обработки CSV-файла
def extract_data_from_csv(name: str, file_data: bytes) -> list:
    """
    Извлекает строки из CSV-файла и возвращает их списком объектов GroupModel.

    :param name: Название группы.
    :param file_data: Байтовое содержимое CSV.
    :return: Список объектов GroupModel.
    """
    file_str = file_data.decode("utf-8")  # Декодируем байты в строку
    file_string = StringIO(file_str)  # Создаем поток данных StringIO
    csv_reader = csv.reader(file_string)  # Читаем CSV
    next(csv_reader)  # Пропускаем заголовок
    
    # Создаём объекты GroupModel из строк CSV
    chanel_name = [
        GroupModel(group_name=name, chat_name=row[0]) for row in csv_reader if row
    ]
    return chanel_name
