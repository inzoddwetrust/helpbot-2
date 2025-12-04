import os
from pathlib import Path
from typing import List, Set


class ProjectTree:
    """
    Класс для создания дерева файлов проекта с исключением ненужных файлов и директорий.
    Исключает сам модуль и файл с результатом.
    Полезно для анализа структуры проекта перед загрузкой в нейронку.
    """

    def __init__(self, root_dir: str = ".", ignore_patterns: List[str] = None):
        """
        Инициализация генератора дерева.

        Args:
            root_dir (str): Корневая директория проекта (по умолчанию текущая).
            ignore_patterns (List[str]): Список паттернов для игнорирования.
                                        Если None, используется стандартный список.
        """
        self.root_dir = Path(root_dir).resolve()
        self.ignore_patterns = set(ignore_patterns) if ignore_patterns else self._default_ignore_patterns()
        # Добавляем сам модуль в игнорируемые файлы
        self.ignore_patterns.add("project_tree.py")
        self.output_file = None  # Будет установлено в generate_tree

    def _default_ignore_patterns(self) -> Set[str]:
        """
        Возвращает стандартный набор игнорируемых файлов и директорий.

        Returns:
            Set[str]: Множество игнорируемых паттернов.
        """
        return {
            "__pycache__",
            "venv",
            ".venv",
            ".git",
            ".idea",
            "node_modules",
            "dist",
            "build",
            "*.pyc",
            "*.pyo",
            "*.egg-info",
            ".DS_Store",
            ".pytest_cache",
            ".tox",
            "*.log",
            "*.cache",
            "*.bak",
        }

    def _should_ignore(self, path: Path) -> bool:
        """
        Проверяет, нужно ли игнорировать файл или директорию.

        Args:
            path (Path): Путь к файлу или директории.

        Returns:
            bool: True, если путь нужно игнорировать.
        """
        name = path.name
        # Проверяем, является ли файл выходным файлом
        if self.output_file and name == self.output_file:
            return True
        # Проверяем паттерны игнорирования
        for pattern in self.ignore_patterns:
            if pattern.startswith("*") and name.endswith(pattern[1:]):
                return True
            if name == pattern:
                return True
        return False

    def generate_tree(self, output_file: str = None) -> str:
        """
        Генерирует строковое представление дерева файлов проекта.

        Args:
            output_file (str, optional): Если указан, дерево сохраняется в файл.

        Returns:
            str: Строковое представление дерева.
        """
        self.output_file = output_file  # Сохраняем имя выходного файла
        tree_lines = []
        self._build_tree(self.root_dir, "", tree_lines)

        tree_str = "\n".join(tree_lines)

        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(tree_str)

        self.output_file = None  # Сбрасываем после генерации
        return tree_str

    def _build_tree(self, directory: Path, prefix: str, lines: List[str]) -> None:
        """
        Рекурсивно строит дерево файлов.

        Args:
            directory (Path): Текущая директория.
            prefix (str): Префикс для форматирования строк (отступы).
            lines (List[str]): Список строк дерева.
        """
        try:
            entries = sorted(directory.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
            for index, entry in enumerate(entries):
                if self._should_ignore(entry):
                    continue

                is_last = index == len(entries) - 1
                connector = "└── " if is_last else "├── "
                lines.append(f"{prefix}{connector}{entry.name}")

                if entry.is_dir():
                    new_prefix = prefix + ("    " if is_last else "│   ")
                    self._build_tree(entry, new_prefix, lines)
        except PermissionError:
            lines.append(f"{prefix}├── [Permission Denied]")
        except Exception as e:
            lines.append(f"{prefix}├── [Error: {str(e)}]")


def main():
    """
    Пример использования модуля.
    """
    tree = ProjectTree()
    tree_str = tree.generate_tree("project_tree.txt")
    print(tree_str)


if __name__ == "__main__":
    main()