import sys
import os
import pandas as pd
import json
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QFileDialog, QMessageBox, QHBoxLayout, QFrame, QStackedWidget,
    QComboBox, QMenuBar, QMenu, QTableWidget, QTableWidgetItem, QHeaderView, QTextEdit, QGroupBox, QSlider, QGridLayout 
)
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QIcon, QColor, QFont, QAction, QPixmap
from PySide6.QtWidgets import QSizePolicy
import datetime

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

        self.btn_see_table = QPushButton("История запросов")
        self.btn_see_table.setStyleSheet(button_style())
        self.btn_see_table.setIcon(QIcon.fromTheme("help-faq"))
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

        self.title = QLabel("Конструктор RAG-запросов к языковой модели")
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
        self.chunk_size = ""
        self.overlap = ""
        self.left_text = ""
        self.right_text = ""
        self.config_field_value = ""  # New variable for config field

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

        # Add only save_left_field_button, left_field, right_field to home_layout

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
        self.save_left_field_button.clicked.connect(self.save_and_query_llm)  # Connect to the same function as save_and_query_button
        home_layout.addWidget(self.save_left_field_button, alignment=Qt.AlignTop | Qt.AlignHCenter)

        # Two QTextEdits: left_field and right_field
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

        home_layout.addLayout(fields_layout)

        # Set the stretch factor for the fields_layout to make it occupy remaining space
        home_layout.setStretchFactor(fields_layout, 1)

        self.home_page.setLayout(home_layout)
        self.stacked_widget.addWidget(self.home_page)
        
        #################################
        #   # Add a new button for saving and querying
        # self.save_and_query_button = QPushButton("Сохранить и запросить LLM")
        # self.save_and_query_button.setFixedSize(250, 50)
        # self.save_and_query_button.setFont(QFont("Arial", 12))
        # self.save_and_query_button.setStyleSheet("""
        #     QPushButton {
        #         background-color: #3498db;
        #         color: white;
        #         border: none;
        #         border-radius: 5px;
        #     }
        #     QPushButton:hover {
        #         background-color: #2980b9;
        #     }
        # """)
        # self.save_and_query_button.clicked.connect(self.save_and_query_llm)
        
        # # Add this button to your layout (adjust as needed based on your existing layout)
        # fields_layout.addWidget(self.save_and_query_button)
        ################################


        # Settings Page
        self.settings_page = QWidget()
        settings_layout = QVBoxLayout()

        # Moved elements from Home to Settings

        # Start of Selection
        # Top-aligned layout for the selection elements
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

        # Read paths from paths.json
        current_dir = os.getcwd()
        paths_file = os.path.join(current_dir, 'paths.json')
        paths = {}
        if os.path.exists(paths_file):
            try:
                with open(paths_file, 'r', encoding='utf-8') as f:
                    paths = json.load(f)  # Load the JSON data directly
            except (UnicodeDecodeError, json.JSONDecodeError):
                # Handle potential decoding errors or JSON format errors
                print("Error reading paths from paths.json")

        # Start of Selection
        # Create a QFrame to hold all the fields
        fields_frame = QFrame()
        fields_frame.setFrameStyle(QFrame.Box | QFrame.Sunken)
        fields_frame.setLineWidth(1)
        fields_frame.setMidLineWidth(0)
        fields_frame.setStyleSheet("QFrame { background-color: transparent; border: 1px solid #CCCCCC; }")
        
        fields_layout = QVBoxLayout(fields_frame)
        
        # Sample descriptions for each field
        input_description = QLabel("<b>Папка с исходными файлами</b>")
        input_description.setFont(QFont("Arial", 12))
        input_description.setStyleSheet("border: none;")
        input_icon = QLabel()
        input_icon.setPixmap(QIcon.fromTheme("help-about").pixmap(QSize(16, 16)))
        input_icon.setToolTip("<p> Папка с исходными документами, <br/> для которых нужно создать векторные представления в БД</p>")
        input_icon.setStyleSheet("border: none;")
        
        markdown_description = QLabel("<b>Папка с Markdown файлами</b>")
        markdown_description.setFont(QFont("Arial", 12))
        markdown_description.setStyleSheet("border: none;")
        markdown_icon = QLabel()
        markdown_icon.setPixmap(QIcon.fromTheme("help-about").pixmap(QSize(16, 16)))
        markdown_icon.setToolTip("Папка с исходными конвертированными <br/> файлами markdown разметкой")
        markdown_icon.setStyleSheet("border: none;")
        
        output_description = QLabel("<b>Папка для базы данных с индексом</b>")
        output_description.setFont(QFont("Arial", 12))
        output_icon = QLabel()
        output_icon.setPixmap(QIcon.fromTheme("help-about").pixmap(QSize(16, 16)))
        output_icon.setToolTip("Папка для базы данных с векторынми представлениями")
        
        extra_description = QLabel("<b>Путь к метасправочнику</b>")
        extra_description.setFont(QFont("Arial", 12))
        extra_icon = QLabel()
        extra_icon.setPixmap(QIcon.fromTheme("help-about").pixmap(QSize(16, 16)))
        extra_icon.setToolTip('''Путь к метасправочнику, в котором содержится информация в каких документах искать информацию. <br/> 
                              Например, если в вопросе указана конкретная модель БВД, то ответ будет основан на тех.документации для этого БВД''')
        
        config_description = QLabel("<b>Путь к конфигурационному файлу</b>")
        config_description.setFont(QFont("Arial", 12))
        config_icon = QLabel()
        config_icon.setPixmap(QIcon.fromTheme("help-about").pixmap(QSize(16, 16)))
        config_icon.setToolTip("Путь к конфигурационному файлу")

        # Input Folder
        input_desc_icon_layout = QHBoxLayout()
        input_desc_icon_layout.addWidget(input_description)
        input_desc_icon_layout.addWidget(input_icon)
        input_desc_icon_layout.addStretch()
        
        input_layout = QVBoxLayout()
        input_layout.addLayout(input_desc_icon_layout)  # Added to input_layout instead of fields_layout

        input_field_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setText(paths.get('Source Files Folder', ''))
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
        fields_layout.addLayout(input_layout)

        # Markdown Folder
        markdown_layout = QVBoxLayout()
        markdown_desc_icon_layout = QHBoxLayout()
        markdown_desc_icon_layout.addWidget(markdown_description)
        markdown_desc_icon_layout.addWidget(markdown_icon)
        markdown_desc_icon_layout.addStretch()
        markdown_layout.addLayout(markdown_desc_icon_layout)

        markdown_field_layout = QHBoxLayout()
        self.markdown_field = QLineEdit()
        self.markdown_field.setText(paths.get('Markdown Folder', ''))
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
        fields_layout.addLayout(markdown_layout)

        input_output_markdown_layout.addWidget(fields_frame)

        # Output and Extra Field Layout
        output_extra_layout = QVBoxLayout()

        # Output Folder
        output_layout = QVBoxLayout()
        output_desc_icon_layout = QHBoxLayout()
        output_desc_icon_layout.addWidget(output_description)
        output_desc_icon_layout.addWidget(output_icon)
        output_desc_icon_layout.addStretch()
        output_layout.addLayout(output_desc_icon_layout)

        output_field_layout = QHBoxLayout()
        self.output_field = QLineEdit()
        self.output_field.setText(paths.get('Output Folder', ''))
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
        extra_desc_icon_layout = QHBoxLayout()
        extra_desc_icon_layout.addWidget(extra_description)
        extra_desc_icon_layout.addWidget(extra_icon)
        extra_desc_icon_layout.addStretch()
        extra_layout.addLayout(extra_desc_icon_layout)

        extra_field_layout = QHBoxLayout()
        self.extra_field = QLineEdit()
        self.extra_field.setText(paths.get('Extra Path', ''))
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

        # Configuration File Field
        config_layout = QVBoxLayout()
        config_desc_icon_layout = QHBoxLayout()
        config_desc_icon_layout.addWidget(config_description)
        config_desc_icon_layout.addWidget(config_icon)
        config_desc_icon_layout.addStretch()
        config_layout.addLayout(config_desc_icon_layout)

        config_field_layout = QHBoxLayout()
        self.config_field = QLineEdit()
        self.config_field.setText(paths.get('Config File Path', ''))
        self.config_field.setFixedHeight(40)
        self.config_field.setFixedWidth(400)  # Set width to 400 pixels
        self.config_field.setFont(QFont("Arial", 12))
        self.config_field.textChanged.connect(self.update_config_field)
        config_field_layout.addWidget(self.config_field)
        self.browse_config_button = QPushButton("Найти")
        self.browse_config_button.setFixedSize(80, 40)
        self.browse_config_button.setFont(QFont("Arial", 12))
        self.browse_config_button.clicked.connect(self.browse_config_folder)
        config_field_layout.addWidget(self.browse_config_button)
        config_layout.addLayout(config_field_layout)
        output_extra_layout.addLayout(config_layout)

        input_output_markdown_layout.addLayout(output_extra_layout)

        # Add input_output_markdown_layout to top_layout
        top_layout.addLayout(input_output_markdown_layout)
        
        # Add vertical spacing (3 times the original)
        top_layout.addSpacing(60)  # Assuming original spacing was 20, now it's 60

        # Create a new layout for the additional fields
        additional_fields_layout = QVBoxLayout()

        # Create a QGroupBox for the additional fields
        additional_fields_group = QGroupBox()
        additional_fields_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
            }
        """)
        additional_fields_layout = QVBoxLayout(additional_fields_group)

        # Start of Selection
        # Text chunk size field with QSlider and labels
        chunk_size_layout = QVBoxLayout()
        chunk_size_desc_icon_layout = QHBoxLayout()
        chunk_size_description = QLabel("<b>размер векторного представления текста</b>")
        chunk_size_description.setFont(QFont("Arial", 12))
        chunk_size_desc_icon_layout.addWidget(chunk_size_description)
        
        # Add QIcon for chunk_size_slider
        chunk_size_icon = QLabel()
        chunk_size_icon.setPixmap(QIcon.fromTheme("help-about").pixmap(QSize(16, 16)))
        chunk_size_icon.setToolTip("Используйте этот слайдер для настройки размера фрагмента для векторного представления текста.")
        chunk_size_desc_icon_layout.addWidget(chunk_size_icon)
        chunk_size_desc_icon_layout.addStretch()
        chunk_size_layout.addLayout(chunk_size_desc_icon_layout)

        # Initialize the QSlider for chunk size
        self.chunk_size_slider = QSlider(Qt.Horizontal)
        self.chunk_size_slider.setRange(500, 5000)  # Set range from 500 to 5000
        self.chunk_size_slider.setSingleStep(500)    # Step of 500
        self.chunk_size_slider.setTickInterval(500)
        self.chunk_size_slider.setTickPosition(QSlider.TicksBelow)
        self.chunk_size_slider.setValue(int(paths.get('Chunk Size', 500)))  # Default value
        self.chunk_size_slider.valueChanged.connect(self.update_chunk_size)
        self.chunk_size_slider.setToolTip("Размер фрагмента текста для векторного представления (в символах)")
        chunk_size_layout.addWidget(self.chunk_size_slider)
        
        # Define and add chunk size labels below the slider
        chunk_size_values = [500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000]
        chunk_size_labels_layout = QHBoxLayout()
        
        for value in chunk_size_values:
            label = QLabel(str(value))
            label.setFont(QFont("Arial", 10))
            label.setAlignment(Qt.AlignCenter)
            chunk_size_labels_layout.addWidget(label)
        chunk_size_layout.addLayout(chunk_size_labels_layout)
        

        additional_fields_layout.addLayout(chunk_size_layout)
        
        # Add vertical spacing (3 times the original)
        chunk_size_layout.addSpacing(40)  # Assuming original spacing was 20, now it's 60

        # Text overlap field with QSlider and labels
        overlap_layout = QVBoxLayout()
        overlap_desc_icon_layout = QHBoxLayout()
        overlap_description = QLabel("<b>'перекрытие' текста, %</b>")
        overlap_description.setFont(QFont("Arial", 12))
        overlap_desc_icon_layout.addWidget(overlap_description)
        
        # Add QIcon for overlap_slider
        overlap_icon = QLabel()
        overlap_icon.setPixmap(QIcon.fromTheme("help-about").pixmap(QSize(16, 16)))
        overlap_icon.setToolTip("Используйте этот слайдер для настройки процента перекрытия текста.")
        overlap_desc_icon_layout.addWidget(overlap_icon)
        overlap_desc_icon_layout.addStretch()
        overlap_layout.addLayout(overlap_desc_icon_layout)
        
        # Initialize the QSlider for text overlap
        self.overlap_slider = QSlider(Qt.Horizontal)
        self.overlap_slider.setRange(10, 50)    # Set range from 10 to 50
        self.overlap_slider.setSingleStep(10)   # Step of 10
        self.overlap_slider.setTickInterval(10)
        self.overlap_slider.setTickPosition(QSlider.TicksBelow)
        self.overlap_slider.setValue(int(paths.get('Text Overlap', 10)))  # Default value
        self.overlap_slider.valueChanged.connect(self.update_overlap)
        self.overlap_slider.setToolTip("Adjust the text overlap percentage")
        overlap_layout.addWidget(self.overlap_slider)
        
        # Define and add overlap labels below the slider
        overlap_values = [10, 20, 30, 40, 50]
        overlap_labels_layout = QHBoxLayout()
        
        for value in overlap_values:
            label = QLabel(str(value))
            label.setFont(QFont("Arial", 10))
            label.setAlignment(Qt.AlignCenter)
            overlap_labels_layout.addWidget(label)
        overlap_layout.addLayout(overlap_labels_layout)
        
        additional_fields_layout.addLayout(overlap_layout)
        
        # Add vertical spacing (3 times the original)
        overlap_layout.addSpacing(60)  # Assuming original spacing was 20, now it's 60

        # LLM Model selection dropdown
        model_layout = QVBoxLayout()
        model_description = QLabel("<b>Выберите LLM модель</b>")
        model_description.setFont(QFont("Arial", 12))
        model_layout.addWidget(model_description)
        self.model_dropdown = QComboBox()
        self.model_dropdown.addItems(["Claude Sonnet", "Claude Haiku", "Gigachat Sber", "Yandex GPT"])
        self.model_dropdown.setCurrentText("Claude Sonnet")
        self.model_dropdown.setFixedHeight(40)
        self.model_dropdown.setFixedWidth(200)
        self.model_dropdown.setFont(QFont("Arial", 12))
        model_layout.addWidget(self.model_dropdown)
        additional_fields_layout.addLayout(model_layout)

        # Add the QGroupBox to the input_output_markdown_layout
        input_output_markdown_layout.addWidget(additional_fields_group)

        # Add button above the System Prompt Field
        self.save_button = QPushButton("Создать векторные представления документов")
        self.save_button.setFixedSize(400, 40)  # Set width to 300 and height to 40
        self.save_button.setFont(QFont("Arial", 12))
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
        """)
        top_layout.addWidget(self.save_button)

        # Add vertical spacing (3 times the original)
        top_layout.addSpacing(60)  # Assuming original spacing was 20, now it's 60

        # System Prompt Field
        system_prompt_layout = QVBoxLayout()
        system_prompt_desc_icon_layout = QHBoxLayout()
        system_prompt_description = QLabel("<b>Системный промпт</b>")
        system_prompt_description.setFont(QFont("Arial", 12))
        system_prompt_desc_icon_layout.addWidget(system_prompt_description)
        
        # Add QIcon for system_prompt_description
        system_prompt_icon = QLabel()
        system_prompt_icon.setPixmap(QIcon.fromTheme("help-about").pixmap(QSize(16, 16)))
        system_prompt_icon.setToolTip("Введите системный промпт для настройки модели.")
        system_prompt_desc_icon_layout.addWidget(system_prompt_icon)
        system_prompt_desc_icon_layout.addStretch()
        system_prompt_layout.addLayout(system_prompt_desc_icon_layout)

        self.system_prompt_field = QTextEdit()  # Initialize the QTextEdit field
        self.system_prompt_field.setPlaceholderText("Системный промпт")
        self.system_prompt_field.setFont(QFont("Arial", 12))
        self.system_prompt_field.setFixedWidth(600)  # Set width to match screen width
        self.system_prompt_field.setFixedHeight(200)  # Set width to match screen width
        system_prompt_layout.addWidget(self.system_prompt_field)

        # Set the system prompt field value from paths.json
        self.system_prompt_field.setText(paths.get('System Prompt', ''))  # Set default to empty string if not found

        # Add the system prompt layout to the input_output_markdown_layout
        top_layout.addLayout(system_prompt_layout)

        
        # Create Index Button (Moved to Settings Page)
        self.create_button = QPushButton("Сохранить конфигурационный файл")
        self.create_button.setFixedSize(300, 60)  # Set width to 200 and height to 60
        self.create_button.setFont(QFont("Arial", 12))
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

        settings_layout.addLayout(top_layout)

        self.settings_page.setLayout(settings_layout)
        self.stacked_widget.addWidget(self.settings_page)

        # About Page
        self.about_page = QWidget()
        about_layout = QVBoxLayout()
        about_label = QLabel("Инструкция для пользователя: как работать с LLM для настройки ИИ-агента техподдержки")
        about_label.setFont(QFont("Arial", 16))
        about_layout.addWidget(about_label)

        # Create a QLabel to display the image
        image_label = QLabel()

        # Load the image (ensure the file path is correct)
        pixmap = QPixmap(r"C:\Users\134\Downloads\Диаграмма без названия.drawio.png")

        # Calculate the aspect ratio of the original image
        aspect_ratio = pixmap.width() / pixmap.height()

        # Set a maximum width for the image (adjust as needed)
        max_width = 800

        # Scale the image while maintaining aspect ratio
        scaled_pixmap = pixmap.scaledToWidth(max_width, Qt.SmoothTransformation)

        # Set the scaled QPixmap on the QLabel
        image_label.setPixmap(scaled_pixmap)

        # Allow the image to resize with the window, but maintain aspect ratio
        image_label.setScaledContents(False)
        image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        image_label.setAlignment(Qt.AlignCenter)

        # Add the QLabel to the layout
        about_layout.addWidget(image_label)

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

    def update_left_text(self):
        self.left_text = self.left_field.toPlainText()

    def update_right_text(self):
        self.right_text = self.right_field.toPlainText()

    def update_source_files_path(self, text):
        self.source_files_path = text

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

    def browse_excel_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выбрать Excel файл", "", "Excel Files (*.xlsx *.xls)"
        )
        if file_path:
            self.path_field.setText(file_path)
            
    def browse_config_folder(self):
        # Open a file dialog to select a configuration file
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Выбрать конфигурационный файл", 
            "", 
            "Config Files (*.json *.yaml *.cfg);;All Files (*)"
        )
        if file_path:
            self.config_field.setText(file_path)
            self.config_field_value = file_path
            
    def browse_markdown_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Выбрать папку с markdown файлами")
        if folder_path:
            self.markdown_field.setText(folder_path)  

    def update_db_index_path(self, text):
        self.db_index_path = text

    def update_markdown_files_path(self, text):
        self.markdown_files_path = text

    def save_left_field_content(self):
        try:
            current_dir = os.getcwd()
            paths_file = os.path.join(current_dir, 'paths.txt')
            
            with open(paths_file, 'a', encoding='utf-8') as f:
                f.write(f"Question: {self.left_text}\n")
            
            QMessageBox.information(self, "Сохранено", "Вопрос успешно сохранен в файл paths.txt")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить вопрос: {str(e)}")                    
    
    # Add these new methods
    def update_chunk_size(self, value):
        self.chunk_size = value

    def update_overlap(self, value):
        self.overlap = value

    def update_config_field(self, text):
        self.config_field_value = text

    # Modify the run_script method to include the new fields
    def run_script(self):
        input_folder = self.input_field.text()
        output_folder = self.output_field.text()
        markdown_folder = self.markdown_field.text()
        extra_path = self.extra_field.text()
        chunk_size = self.chunk_size_slider.value()
        overlap = self.overlap_slider.value()
        model_dropdown = self.model_dropdown.currentText()
        config_folder = self.config_field_value  # Use the updated config_field_value
        system_prompt = self.system_prompt_field.toPlainText()  # Get the system prompt text

        try:
            # Define the path for paths.json in the current working directory
            current_dir = os.getcwd()
            paths_file = os.path.join(current_dir, 'paths.json')
            
            # Save all field values to paths.json
            data = {
                "Source Files Folder": input_folder,
                "Output Folder": output_folder,
                "Markdown Folder": markdown_folder,
                "Extra Path": extra_path,
                "Chunk Size": chunk_size,
                "Text Overlap": overlap,
                "Model": model_dropdown,
                "Config File Path": config_folder,
                "System Prompt": system_prompt  # Add the system prompt to the data
            }
            
            with open(paths_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            if os.path.exists(paths_file):
                file_size = os.path.getsize(paths_file)
                QMessageBox.information(
                    self, 
                    "File Saved", 
                    f"paths.json was successfully created at {paths_file}\nFile size: {file_size} bytes"
                )
            else:
                QMessageBox.warning(
                    self, 
                    "File Not Found", 
                    f"paths.json was not found at {paths_file}"
                )

            # Run the external python script with the folder paths as arguments
            subprocess.run([
                'python', 
                r"C:\Users\134\Documents\Python Scripts\test_script_for_gui_button.py",
                '--input_folder', input_folder,
                '--output_folder', output_folder,
                '--markdown_folder', markdown_folder,
                '--extra_path', extra_path,
                '--config_path', config_folder  # Pass the config path
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
                    item.setTextAlignment(Qt.AlignTop | Qt.AlignLeft)
                    self.table_widget.setItem(i, j, item)

            # Set column widths
            self.table_widget.setColumnWidth(0, 200)
            self.table_widget.setColumnWidth(1, 300)
            self.table_widget.setColumnWidth(2, 600)

            # Enable word wrap for all items
            self.table_widget.setWordWrap(True)

            # Adjust row heights to fit content
            for row in range(self.table_widget.rowCount()):
                self.table_widget.resizeRowToContents(row)

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

    #######################################################
    def save_and_query_llm(self):
        try:
            # First, save the content
            self.save_left_field_content()

            # Then, query the LLM
            text_to_send_tech_support = self.left_field.toPlainText()
            
            # Run the query_LLM.py script
            result = subprocess.run(
                ['python', r'C:\Users\134\Documents\Python Scripts\query_LLM.py'],
                input=text_to_send_tech_support,
                text=True,
                capture_output=True,
                check=True
            )

            # Get the output from the script
            claude_reply_tech_support = result.stdout.strip()

            # Update the right field with the response
            self.right_field.setPlainText(claude_reply_tech_support)

            QMessageBox.information(self, "Успех", "Запрос к LLM выполнен успешно")
            
            # save history pf questins and answers
            self.save_left_and_right_field_content()
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при выполнении скрипта LLM: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Неожиданная ошибка: {str(e)}")

    def save_left_and_right_field_content(self):
        try:
            import pandas as pd
            import os

            current_dir = os.getcwd()
            excel_file = os.path.join(current_dir, 'query_history.xlsx')

            # Check if the Excel file exists, if not, create it with headers
            if not os.path.isfile(excel_file):
                # Create a DataFrame with headers
                initial_data = pd.DataFrame(columns=['Question', 'Response'])
                initial_data.to_excel(excel_file, index=False)

            # Create a DataFrame to hold the question and response
            question_data = pd.DataFrame({
                'Время': [datetime.datetime.now()],
                'Вопрос': [self.left_field.toPlainText()],
                'Ответ модели': [self.right_field.toPlainText()]
            })
            
            # Append the question and response to the Excel file
            with pd.ExcelWriter(excel_file, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
                question_data.to_excel(writer, index=False, header=False, startrow=writer.sheets['Sheet1'].max_row)

            QMessageBox.information(self, "Сохранено", "Вопрос и ответ успешно сохранены в файл query_history.xlsx")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить вопрос и ответ: {str(e)}")
    

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