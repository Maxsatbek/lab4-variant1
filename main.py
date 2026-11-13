
import os
from datetime import datetime
from pathlib import Path


def ask_int(prompt, minimum=0):
    """Запрашивает целое число и проверяет его значение."""
    while True:
        try:
            value = int(input(prompt))

            if value < minimum:
                print(f"Введите число не меньше {minimum}.")
                continue

            return value

        except ValueError:
            print("Ошибка: необходимо ввести целое число.")


def ask_yes_no(prompt):
    """Запрашивает ответ Да или Нет."""
    while True:
        answer = input(prompt).strip().lower()

        if answer in ("да", "д", "yes", "y"):
            return True

        if answer in ("нет", "н", "no", "n"):
            return False

        print("Введите Да или Нет.")


def read_source_file(file_path):
    """Читает текстовый файл с поддержкой UTF-8 и Windows-1251."""
    if not file_path.is_file():
        raise FileNotFoundError(
            f"Файл не найден: {file_path}"
        )

    for encoding in ("utf-8-sig", "cp1251"):
        try:
            return file_path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue

    raise UnicodeError(
        "Не удалось определить кодировку файла."
    )


def create_pages(
    text,
    source_path,
    lines_per_page,
    left_margin,
    show_datetime,
    show_file_info
):
    """Разбивает документ на страницы и форматирует их."""

    current_time = datetime.now()

    date_text = current_time.strftime("%d.%m.%Y")
    time_text = current_time.strftime("%H:%M:%S")
    datetime_text = current_time.strftime("%d.%m.%Y %H:%M:%S")

    header = []

    # Вывод текущей даты и времени
    if show_datetime:
        header.append(
            f"Дата и время печати: {datetime_text}"
        )

    # Вывод имени исходного файла, даты и времени
    if show_file_info:
        header.append(
            f"Исходный файл: {source_path.name}"
        )
        header.append(
            f"Дата: {date_text}    Время: {time_text}"
        )

    # Проверка доступного количества строк
    content_lines_per_page = lines_per_page - len(header)

    if content_lines_per_page <= 0:
        raise ValueError(
            "Слишком мало строк на странице для выбранного заголовка."
        )

    # Получение строк исходного документа
    text_lines = text.splitlines()

    if not text_lines:
        text_lines = [""]

    pages = []

    # Разделение текста на страницы
    for start in range(0, len(text_lines), content_lines_per_page):

        page_content = text_lines[
            start:start + content_lines_per_page
        ]

        # Добавление заголовка
        page_lines = header + page_content

        # Дополнение страницы пустыми строками
        while len(page_lines) < lines_per_page:
            page_lines.append("")

        # Добавление левого отступа
        margin = " " * left_margin

        formatted_page = [
            margin + line for line in page_lines
        ]

        pages.append("\n".join(formatted_page))

    return pages


def show_on_screen(pages):
    """Выводит документ на экран постранично."""

    for index, page in enumerate(pages, start=1):

        print("\n" + "=" * 45)
        print(f"СТРАНИЦА {index} ИЗ {len(pages)}")
        print("=" * 45)

        print(page)

        if index < len(pages):
            input(
                "\nНажмите Enter для перехода к следующей странице..."
            )


def save_to_file(pages, output_path):
    """Сохраняет отформатированный документ в файл."""

    formatted_text = "\n\f\n".join(pages)

    output_path.write_text(
        formatted_text,
        encoding="utf-8"
    )

    print(f"\nДокумент сохранен: {output_path.resolve()}")


def print_document(pages, source_path):
    """Передает документ на печать в Windows."""

    if os.name != "nt":
        print(
            "Автоматическая отправка на принтер "
            "в этой операционной системе не поддерживается."
        )
        return

    output_path = source_path.with_name(
        source_path.stem + "_for_print.txt"
    )

    save_to_file(pages, output_path)

    try:
        os.startfile(str(output_path), "print")

        print(
            "\nФайл передан приложению Windows "
            "для печати на принтере по умолчанию."
        )
        print(
            "Проверьте очередь печати и настройки принтера."
        )

    except OSError as error:
        print("\nНе удалось отправить файл на печать.")
        print("Ошибка:", error)
        print(
            "Откройте созданный файл вручную и распечатайте его."
        )


def main():
    print("=" * 50)
    print("       ПРОГРАММА ФОРМАТИРОВАНИЯ ДОКУМЕНТОВ")
    print("=" * 50)

    # 1. Получение имени исходного файла
    file_name = input(
        "\nВведите имя исходного файла: "
    ).strip().strip('"')

    source_path = Path(file_name).expanduser()

    try:
        text = read_source_file(source_path)

    except (FileNotFoundError, UnicodeError, OSError) as error:
        print("\nОшибка чтения файла:", error)
        return

    print("\nФайл успешно прочитан.")

    # 2. Выбор способа вывода
    print("\nВыберите способ вывода:")
    print("1 - На экран")
    print("2 - В другой текстовый файл")
    print("3 - На принтер")

    while True:
        mode = input("Ваш выбор: ").strip()

        if mode in ("1", "2", "3"):
            break

        print("Выберите вариант 1, 2 или 3.")

    # 3. Настройка количества строк
    lines_per_page = ask_int(
        "\nВведите количество строк на странице: ",
        minimum=1
    )

    # 4. Настройка левого отступа
    left_margin = ask_int(
        "Введите количество пробелов слева: ",
        minimum=0
    )

    # 5. Дополнительные параметры
    show_datetime = ask_yes_no(
        "\nДобавить текущую дату и время печати? (Да/Нет): "
    )

    show_file_info = ask_yes_no(
        "Добавить имя файла, дату и время в заголовок? (Да/Нет): "
    )

    # 6. Формирование страниц
    while True:
        try:
            pages = create_pages(
                text,
                source_path,
                lines_per_page,
                left_margin,
                show_datetime,
                show_file_info
            )
            break

        except ValueError as error:
            print("\nОшибка:", error)
            print(
                "Увеличьте количество строк на странице."
            )

            lines_per_page = ask_int(
                "Введите новое количество строк: ",
                minimum=1
            )

    print(
        f"\nДокумент подготовлен. Количество страниц: {len(pages)}"
    )

    # 7. Вывод результата
    if mode == "1":

        show_on_screen(pages)

    elif mode == "2":

        default_name = source_path.stem + "_formatted.txt"

        output_name = input(
            f"\nВведите имя выходного файла "
            f"[{default_name}]: "
        ).strip().strip('"')

        if not output_name:
            output_name = default_name

        output_path = Path(output_name).expanduser()

        if output_path.resolve() == source_path.resolve():
            print(
                "Ошибка: нельзя перезаписывать исходный файл."
            )
            return

        try:
            save_to_file(pages, output_path)

        except OSError as error:
            print("Ошибка сохранения:", error)

    elif mode == "3":

        print_document(pages, source_path)

    print("\nРабота программы завершена.")


if __name__ == "__main__":
    main()
