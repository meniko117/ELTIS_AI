import sys
import os
import pandas as pd
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QFileDialog, QMessageBox, QHBoxLayout, QFrame, QStackedWidget,
    QComboBox, QMenuBar, QMenu, QTableWidget, QTableWidgetItem, QHeaderView, QTextEdit 
)
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QIcon, QColor, QFont, QAction
from PySide6.QtWidgets import QSizePolicy

import subprocess

class Sidebar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_collapsed = False
        self.expanded_width = 200
        self.collapsed_width = 50
        self.setFixedWidth(self.expanded_width)
        self.setStyleSheet("""
            background-color: #2c3e50;
        """)

        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Toggle Button
        self.toggle_button = QPushButton("☰")
        self.toggle_button.setFixedHeight(40)
        self.toggle_button.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: #2c3e50;
                border: none;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
        """)
        self.toggle_button.clicked.connect(self.toggle_sidebar)
        self.main_layout.addWidget(self.toggle_button)

        # Create a container widget for the buttons
        self.button_container = QWidget()
        self.button_layout = QVBoxLayout(self.button_container)
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        self.button_layout.setSpacing(0)

        # Add navigation buttons
        self.btn_home = QPushButton("Домой")
        self.btn_home.setStyleSheet(button_style())
        self.btn_home.setIcon(QIcon.fromTheme("go-home"))
        self.btn_home.setIconSize(QSize(24, 24))
        self.button_layout.addWidget(self.btn_home)

        self.btn_settings = QPushButton("Настройки")
        self.btn_settings.setStyleSheet(button_style())
        self.btn_settings.setIcon(QIcon.fromTheme("document-new"))
        self.btn_settings.setIconSize(QSize(24, 24))
        self.button_layout.addWidget(self.btn_settings)

        self.btn_about = QPushButton("О приложении")
        self.btn_about.setStyleSheet(button_style())
        self.btn_about.setIcon(QIcon.fromTheme("help-about"))
        self.btn_about.setIconSize(QSize(24, 24))
        self.button_layout.addWidget(self.btn_about)

        self.btn_see_table = QPushButton("Посмотреть таблицу")
        self.btn_see_table.setStyleSheet(button_style())
        self.btn_see_table.setIcon(QIcon.fromTheme("insert-table"))
        self.btn_see_table.setIconSize(QSize(24, 24))
        self.button_layout.addWidget(self.btn_see_table)

        self.main_layout.addWidget(self.button_container)

        # Spacer
        self.main_layout.addStretch()

        self.setLayout(self.main_layout)

    def toggle_sidebar(self):
        self.animation = QPropertyAnimation(self, b"minimumWidth")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        if self.is_collapsed:
            # Expand sidebar
            self.animation.setStartValue(self.collapsed_width)
            self.animation.setEndValue(self.expanded_width)
            self.animation.start()
            self.expand_buttons()
            self.is_collapsed = False
        else:
            # Collapse sidebar
            self.animation.setStartValue(self.expanded_width)
            self.animation.setEndValue(self.collapsed_width)
            self.animation.start()
            self.collapse_buttons()
            self.is_collapsed = True

    def collapse_buttons(self):
        self.btn_home.setText("")
        self.btn_home.setToolTip("Домой")
        self.btn_settings.setText("")
        self.btn_settings.setToolTip("Настройки")
        self.btn_about.setText("")
        self.btn_about.setToolTip("О приложении")
        self.btn_see_table.setText("")
        self.btn_see_table.setToolTip("Посмотреть таблицу")

    def expand_buttons(self):
        self.btn_home.setText("Домой")
        self.btn_home.setToolTip("")
        self.btn_settings.setText("Настройки")
        self.btn_settings.setToolTip("")
        self.btn_about.setText("О приложении")
        self.btn_about.setToolTip("")
        self.btn_see_table.setText("Посмотреть таблицу")
        self.btn_see_table.setToolTip("")  # Fixed: Added empty string as argument

def button_style():
    return """
        QPushButton {
            color: white;
            background-color: #34495e;
            padding: 15px;
            border: none;
            text-align: left;
            font-size: 14px;
            height: 40px;
        }
        QPushButton:hover {
            background-color: #2c3e50;
        }
    """

class Header(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(60)
        self.setStyleSheet("background-color: #34495e;")

        layout = QHBoxLayout()
        layout.setContentsMargins(20, 0, 20, 0)

        self.title = QLabel("E-Цифра Менеджер")
        title_font = QFont("Arial", 20, QFont.Bold)
        self.title.setFont(title_font)
        self.title.setStyleSheet("color: white;")
        layout.addWidget(self.title)

        layout.addStretch()

        # Dropdown Menu
        self.combo = QComboBox()
        self.combo.addItems(["Загрузить остатки", "Анализ продаж", "Финансы"])
        self.combo.setFont(QFont("Arial", 12))
        layout.addWidget(self.combo)

        self.setLayout(layout)

class IndexApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("E-Цифра Менеджер")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("background-color: #ecf0f1;")
        
        # Add this line to create the variable
        self.source_files_path = ""
        self.db_index_path = ""
        self.markdown_files_path = ""
        self.extra_path = ""

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Menu Bar
        self.menu_bar = QMenuBar()
        file_menu = QMenu("Файл", self)
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        self.menu_bar.addMenu(file_menu)

        edit_menu = QMenu("Редактировать", self)
        copy_action = QAction("Копировать", self)
        paste_action = QAction("Вставить", self)
        edit_menu.addAction(copy_action)
        edit_menu.addAction(paste_action)
        self.menu_bar.addMenu(edit_menu)

        main_layout.addWidget(self.menu_bar)

        # Header
        self.header = Header()
        main_layout.addWidget(self.header)

        # Content Layout
        content_layout = QHBoxLayout()

        # Sidebar
        self.sidebar = Sidebar()
        content_layout.addWidget(self.sidebar)

        # Stacked Widget to switch between different pages
        self.stacked_widget = QStackedWidget()
        content_layout.addWidget(self.stacked_widget, 1)  # Make it expandable

        # Home Page
        self.home_page = QWidget()
        home_layout = QVBoxLayout()

        # Start of Selection
        # Reorganized elements to be at the top of the page

        # Create a top-aligned layout for the selection elements
        top_layout = QVBoxLayout()
        top_layout.setAlignment(Qt.AlignTop)

        # Label
        self.label = QLabel("Выбрать папки для исходных файлов с инструкциями и папку для базы данных с индексом:")
        label_font = QFont("Arial", 16)
        self.label.setFont(label_font)
        top_layout.addWidget(self.label)
        
        # Add vertical spacing (3 times the original)
        top_layout.addSpacing(60)  # Assuming original spacing was 20, now it's 60

        # Create a horizontal layout for input, output, and markdown fields
        input_output_markdown_layout = QHBoxLayout()

        # Input and Markdown Folder Layout
        input_markdown_layout = QVBoxLayout()

         # Read paths from paths.txt
        current_dir = os.getcwd()
        paths_file = os.path.join(current_dir, 'paths.txt')
        paths = {}
        if os.path.exists(paths_file):
            try:
                with open(paths_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            key, value = line.strip().split(': ', 1)
                            paths[key] = value
                        except ValueError:
                            # Skip lines that don't have the expected format
                            continue
            except UnicodeDecodeError:
                # If UTF-8 fails, try with 'cp1251' encoding (Windows Cyrillic)
                with open(paths_file, 'r', encoding='cp1251') as f:
                    for line in f:
                        try:
                            key, value = line.strip().split(': ', 1)
                            paths[key] = value
                        except ValueError:
                            # Skip lines that don't have the expected format
                            continue

        # Sample descriptions for each field
        input_description = QLabel("Папка с исходными файлами")
        input_description.setFont(QFont("Arial", 12))
        markdown_description = QLabel("Папка с Markdown файлами")
        markdown_description.setFont(QFont("Arial", 12))
        output_description = QLabel("Папка для базы данных с индексом")
        output_description.setFont(QFont("Arial", 12))
        extra_description = QLabel("Дополнительная папка")
        extra_description.setFont(QFont("Arial", 12))

        # Input Folder
        input_layout = QVBoxLayout()
        input_layout.addWidget(input_description)
        input_field_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText(paths.get('Source Files Folder', ''))
        self.input_field.setFixedHeight(40)
        self.input_field.setFixedWidth(400)  # Set width to 400 pixels
        self.input_field.setFont(QFont("Arial", 12))
        self.input_field.textChanged.connect(self.update_source_files_path)
        input_field_layout.addWidget(self.input_field)
        self.browse_button = QPushButton("Найти")
        self.browse_button.setFixedSize(80, 40)
        self.browse_button.setFont(QFont("Arial", 12))
        self.browse_button.clicked.connect(self.browse_folder)
        input_field_layout.addWidget(self.browse_button)
        input_layout.addLayout(input_field_layout)
        input_markdown_layout.addLayout(input_layout)

        # Markdown Folder
        markdown_layout = QVBoxLayout()
        markdown_layout.addWidget(markdown_description)
        markdown_field_layout = QHBoxLayout()
        self.markdown_field = QLineEdit()
        self.markdown_field.setPlaceholderText(paths.get('Markdown Folder', ''))
        self.markdown_field.setFixedHeight(40)
        self.markdown_field.setFixedWidth(400)  # Set width to 400 pixels
        self.markdown_field.setFont(QFont("Arial", 12))
        self.markdown_field.textChanged.connect(self.update_markdown_files_path)
        markdown_field_layout.addWidget(self.markdown_field)
        self.browse_markdown_button = QPushButton("Найти")
        self.browse_markdown_button.setFixedSize(80, 40)
        self.browse_markdown_button.setFont(QFont("Arial", 12))
        self.browse_markdown_button.clicked.connect(self.browse_markdown_folder)
        markdown_field_layout.addWidget(self.browse_markdown_button)
        markdown_layout.addLayout(markdown_field_layout)
        input_markdown_layout.addLayout(markdown_layout)

        input_output_markdown_layout.addLayout(input_markdown_layout)

        # Output and Extra Field Layout
        output_extra_layout = QVBoxLayout()

        # Output Folder
        output_layout = QVBoxLayout()
        output_layout.addWidget(output_description)
        output_field_layout = QHBoxLayout()
        self.output_field = QLineEdit()
        self.output_field.setPlaceholderText(paths.get('Output Folder', ''))
        self.output_field.setFixedHeight(40)
        self.output_field.setFixedWidth(400)  # Set width to 400 pixels
        self.output_field.setFont(QFont("Arial", 12))
        self.output_field.textChanged.connect(self.update_db_index_path)
        output_field_layout.addWidget(self.output_field)
        self.browse_output_button = QPushButton("Найти")
        self.browse_output_button.setFixedSize(80, 40)
        self.browse_output_button.setFont(QFont("Arial", 12))
        self.browse_output_button.clicked.connect(self.browse_output_folder)
        output_field_layout.addWidget(self.browse_output_button)
        output_layout.addLayout(output_field_layout)
        output_extra_layout.addLayout(output_layout)

        # Extra Field
        extra_layout = QVBoxLayout()
        extra_layout.addWidget(extra_description)
        extra_field_layout = QHBoxLayout()
        self.extra_field = QLineEdit()
        self.extra_field.setPlaceholderText(paths.get('Extra Path', ''))
        self.extra_field.setFixedHeight(40)
        self.extra_field.setFixedWidth(400)  # Set width to 400 pixels
        self.extra_field.setFont(QFont("Arial", 12))
        self.extra_field.textChanged.connect(self.update_extra_path)
        extra_field_layout.addWidget(self.extra_field)
        self.extra_button = QPushButton("Найти")
        self.extra_button.setFixedSize(80, 40)
        self.extra_button.setFont(QFont("Arial", 12))
        self.extra_button.clicked.connect(self.browse_extra_folder)
        extra_field_layout.addWidget(self.extra_button)
        extra_layout.addLayout(extra_field_layout)
        output_extra_layout.addLayout(extra_layout)

        input_output_markdown_layout.addLayout(output_extra_layout)

        # Add input_output_markdown_layout to top_layout
        top_layout.addLayout(input_output_markdown_layout)
        
        # Create Index Button
        self.create_button = QPushButton("Создать Индекс")
        self.create_button.setFixedSize(200, 60)  # Set width to 200 and height to 60
        self.create_button.setFont(QFont("Arial", 16))
        self.create_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        self.create_button.clicked.connect(self.run_script)
        top_layout.addWidget(self.create_button)

        # Add vertical spacing (3 times the original)
        top_layout.addSpacing(60)  # Assuming original spacing was 20, now it's 60

        # Add a button to save left_field content
        self.save_left_field_button = QPushButton("Отправить вопрос в модель")
        self.save_left_field_button.setFixedSize(300, 60)  # Match the size of create_button
        self.save_left_field_button.setFont(QFont("Arial", 16))
        self.save_left_field_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.save_left_field_button.clicked.connect(self.save_left_field_content)
        top_layout.addWidget(self.save_left_field_button)


        # Start of Selection
        # Add the top_layout to home_layout
        home_layout.addLayout(top_layout)

        # Add two empty fields in one row with maximum height
        fields_layout = QHBoxLayout()
        
        self.left_field = QTextEdit()
        self.left_field.setPlaceholderText("Введите вопрос")
        self.left_field.setFont(QFont("Arial", 12))
        self.left_field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.left_field.setStyleSheet("border: 1px solid #A0A0A0;")  # Darker border
        fields_layout.addWidget(self.left_field)
        self.left_text = ""
        
        self.right_field = QTextEdit()
        self.right_field.setPlaceholderText("Ответ модели")
        self.right_field.setFont(QFont("Arial", 12))
        self.right_field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.right_field.setStyleSheet("border: 1px solid #A0A0A0;")  # Darker border
        fields_layout.addWidget(self.right_field)
        self.right_text = ""
        
        # Connect text changed signals to update variables
        self.left_field.textChanged.connect(self.update_left_text)
        self.right_field.textChanged.connect(self.update_right_text)

        
        # Add the fields_layout to home_layout
        home_layout.addLayout(fields_layout)

        # Set the stretch factor for the fields_layout to make it occupy remaining space
        home_layout.setStretchFactor(fields_layout, 1)


        self.home_page.setLayout(home_layout)
        self.stacked_widget.addWidget(self.home_page)

        # Settings Page
        self.settings_page = QWidget()
        settings_layout = QVBoxLayout()
        settings_label = QLabel("Настройки")
        settings_label.setFont(QFont("Arial", 16))
        settings_layout.addWidget(settings_label)
        self.settings_page.setLayout(settings_layout)
        self.stacked_widget.addWidget(self.settings_page)

        # About Page
        self.about_page = QWidget()
        about_layout = QVBoxLayout()
        about_label = QLabel("Инструкция для пользователя: как работать с LLM для настройки ИИ-агента техподдержки")
        about_label.setFont(QFont("Arial", 16))
        about_layout.addWidget(about_label)
        self.about_page.setLayout(about_layout)
        self.stacked_widget.addWidget(self.about_page)

        # See Table Page
        self.see_table_page = QWidget()
        see_table_layout = QVBoxLayout()

        # Path to the file
        path_layout = QHBoxLayout()
        self.path_label = QLabel("Путь к файлу:")
        self.path_label.setFont(QFont("Arial", 14))
        path_layout.addWidget(self.path_label)

        self.path_field = QLineEdit()
        self.path_field.setPlaceholderText("Введите путь к Excel файлу")
        self.path_field.setFixedHeight(50)
        self.path_field.setFont(QFont("Arial", 14))
        path_layout.addWidget(self.path_field)

        self.upload_button = QPushButton("Загрузить")
        self.upload_button.setFixedHeight(50)
        self.upload_button.setFont(QFont("Arial", 14))
        self.upload_button.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1f6391;
            }
        """)
        self.upload_button.clicked.connect(self.upload_excel)
        path_layout.addWidget(self.upload_button)

        # Optional: Add a "Browse" button for selecting Excel files via dialog
        self.browse_excel_button = QPushButton("Найти")
        self.browse_excel_button.setFixedHeight(50)
        self.browse_excel_button.setFont(QFont("Arial", 14))
        self.browse_excel_button.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1f6391;
            }
        """)
        self.browse_excel_button.clicked.connect(self.browse_excel_file)
        path_layout.addWidget(self.browse_excel_button)

        see_table_layout.addLayout(path_layout)

        # Table Widget
        self.table_widget = QTableWidget()
        self.table_widget.setFont(QFont("Arial", 12))
        self.table_widget.setStyleSheet("""
            QTableWidget {
                background-color: white;
                gridline-color: #bdc3c7;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 4px;
                border: none;
            }
        """)
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setSortingEnabled(True)
        # Allow user to resize columns interactively
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        # Enable horizontal scroll
        self.table_widget.setHorizontalScrollMode(QTableWidget.ScrollPerPixel)
        self.table_widget.setSizeAdjustPolicy(QTableWidget.AdjustToContents)

        # Ensure scrollbars appear as needed
        self.table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        see_table_layout.addWidget(self.table_widget)

        self.see_table_page.setLayout(see_table_layout)
        self.stacked_widget.addWidget(self.see_table_page)

        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

        # Connect sidebar buttons to respective pages
        self.sidebar.btn_home.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.home_page))
        self.sidebar.btn_settings.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.settings_page))
        self.sidebar.btn_about.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.about_page))
        self.sidebar.btn_see_table.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.see_table_page))

        # Add these new methods
    def update_left_text(self):
        self.left_text = self.left_field.toPlainText()

    def update_right_text(self):
        self.right_text = self.right_field.toPlainText()
    # Add this method to update the variable when text changes
    def update_source_files_folder(self, text):
        self.source_files_folder = text

    def browse_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Выбрать папку для загрузки")
        if folder_path:
            self.input_field.setText(folder_path)
            # Update the variable here as well
            self.source_files_folder = folder_path

    def browse_output_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Выбрать папку для выгрузки")
        if folder_path:
            self.output_field.setText(folder_path)

    def browse_excel_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выбрать Excel файл", "", "Excel Files (*.xlsx *.xls)"
        )
        if file_path:
            self.path_field.setText(file_path)
            
    def browse_markdown_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Выбрать папку с markdown файлами")
        if folder_path:
            self.markdown_field.setText(folder_path)  

    def update_source_files_path(self, text):
        self.source_files_path = text

    def update_db_index_path(self, text):
        self.db_index_path = text

    def update_markdown_files_path(self, text):
        self.markdown_files_path = text

    def browse_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Выбрать папку для загрузки")
        if folder_path:
            self.input_field.setText(folder_path)
            self.source_files_path = folder_path

    def browse_output_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Выбрать папку для выгрузки")
        if folder_path:
            self.output_field.setText(folder_path)
            self.db_index_path = folder_path

    def browse_markdown_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Выбрать папку с markdown файлами")
        if folder_path:
            self.markdown_field.setText(folder_path)
            self.markdown_files_path = folder_path  
            
    def save_left_field_content(self):
        try:
            current_dir = os.getcwd()
            paths_file = os.path.join(current_dir, 'paths.txt')
            
            with open(paths_file, 'a', encoding='utf-8') as f:
                f.write(f"Question: {self.left_text}\n")
            
            QMessageBox.information(self, "Сохранено", "Вопрос успешно сохранен в файл paths.txt")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить вопрос: {str(e)}")                    

    def run_script(self):
        input_folder = self.input_field.text()
        output_folder = self.output_field.text()
        markdown_folder = self.markdown_field.text()
        extra_path = self.extra_field.text()

        if not input_folder or not output_folder:
            QMessageBox.warning(self, "Input Error", "Please select both input and output folders.")
            return

        try:
            # Define the path for paths.txt in the current working directory
            current_dir = os.getcwd()
            paths_file = os.path.join(current_dir, 'paths.txt')
            
            # Save all field values to paths.txt
            with open(paths_file, 'w', encoding='utf-8') as f:
                f.write(f"Source Files Folder: {input_folder}\n")
                f.write(f"Output Folder: {output_folder}\n")
                f.write(f"Markdown Folder: {markdown_folder}\n")
                f.write(f"Extra Path: {extra_path}\n")

            # Verify that the file was created
            if os.path.exists(paths_file):
                file_size = os.path.getsize(paths_file)
                QMessageBox.information(self, "File Saved", f"paths.txt was successfully created at {paths_file}\nFile size: {file_size} bytes")
            else:
                QMessageBox.warning(self, "File Not Found", f"paths.txt was not found at {paths_file}")

            # Run the external python script with the folder paths as arguments
            subprocess.run([
                'python', r"C:\Users\134\Documents\Python Scripts\test_script_for_gui_button.py",
                '--input_folder', input_folder,
                '--output_folder', output_folder,
                '--markdown_folder', markdown_folder,
                '--extra_path', extra_path
            ], check=True)
            QMessageBox.information(self, "Success", "Index creation completed.")
        except IOError as e:
            error_msg = f"Failed to save path: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            QMessageBox.critical(self, "Error", error_msg)
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Error", f"An error occurred while running the script: {str(e)}")
        except Exception as e:
            error_msg = f"An unexpected error occurred: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            QMessageBox.critical(self, "Error", error_msg)

    def upload_excel(self):
        file_path = self.path_field.text()
        if not file_path:
            QMessageBox.warning(self, "Input Error", "Please enter or select the path to the Excel file.")
            return

        if not os.path.isfile(file_path):
            QMessageBox.critical(self, "File Error", "The specified file does not exist.")
            return

        try:
            # Read Excel file using pandas
            df = pd.read_excel(file_path)

            # Clear existing table
            self.table_widget.clear()

            # Set table dimensions
            self.table_widget.setRowCount(df.shape[0])
            self.table_widget.setColumnCount(df.shape[1])
            self.table_widget.setHorizontalHeaderLabels(df.columns.astype(str))

            # Populate table with data
            for i in range(df.shape[0]):
                for j in range(df.shape[1]):
                    item = QTableWidgetItem(str(df.iat[i, j]))
                    self.table_widget.setItem(i, j, item)

            # Adjust column sizes based on content
            self.table_widget.resizeColumnsToContents()

            QMessageBox.information(self, "Отлично!", "Excel файл загружен")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to upload Excel file:\n{str(e)}")

    def update_extra_path(self, text):
        self.extra_path = text

    def browse_extra_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Выбрать папку для метаданных")
        if folder_path:
            self.extra_field.setText(folder_path)
            self.extra_path = folder_path

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Apply a modern stylesheet
    app.setStyleSheet("""
        QMenuBar {
            background-color: #34495e;
            color: white;
        }
        QMenuBar::item:selected {
            background-color: #2c3e50;
        }
        QMenu {
            background-color: #34495e;
            color: white;
        }
        QMenu::item:selected {
            background-color: #2c3e50;
        }
    """)

    window = IndexApp()
    window.show()
    sys.exit(app.exec())