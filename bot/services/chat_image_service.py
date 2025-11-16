"""Сервис для генерации изображений истории чата"""

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from typing import List, Dict, Tuple
import textwrap
import math


class ChatImageService:
    """Сервис для создания изображений истории чата"""
    
    # Параметры изображения
    IMAGE_WIDTH = 1000
    MARGIN = 40
    LINE_SPACING = 8
    MESSAGE_SPACING = 20
    MAX_HEIGHT = 8000  # Максимальная высота одного изображения
    MESSAGE_WIDTH_PERCENT = 0.8  # 80% ширины изображения
    BORDER_RADIUS = 12  # Радиус закругления углов
    
    def _oklch_to_rgb(self, l: float, c: float, h: float) -> Tuple[int, int, int]:
        """Конвертирует OKLCH в RGB"""
        # Конвертация OKLCH -> OKLAB -> Linear RGB -> sRGB
        # Упрощенная версия конвертации
        
        # OKLCH -> OKLAB
        a = c * math.cos(math.radians(h))
        b = c * math.sin(math.radians(h))
        
        # OKLAB -> Linear RGB
        l_ = l + 0.3963377774 * a + 0.2158037573 * b
        m_ = l - 0.1055613458 * a - 0.0638541728 * b
        s_ = l - 0.0894841775 * a - 1.2914855480 * b
        
        l_ = l_ ** 3
        m_ = m_ ** 3
        s_ = s_ ** 3
        
        r = +4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_
        g = -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_
        b = -0.0041960863 * l_ - 0.7034186147 * m_ + 1.7076147010 * s_
        
        # Linear RGB -> sRGB (gamma correction)
        def gamma_correct(x):
            if x <= 0.0031308:
                return 12.92 * x
            else:
                return 1.055 * (x ** (1.0 / 2.4)) - 0.055
        
        r = max(0, min(1, gamma_correct(r)))
        g = max(0, min(1, gamma_correct(g)))
        b = max(0, min(1, gamma_correct(b)))
        
        return (int(r * 255), int(g * 255), int(b * 255))
    
    def __init__(self):
        """Инициализация сервиса"""
        import platform
        import os
        
        # Темный фон из dark темы CSS
        # background: oklch(0.2161 0.0061 56.0434)
        self.BG_COLOR = self._oklch_to_rgb(0.2161, 0.0061, 56.0434)
        
        # foreground: oklch(0.9699 0.0013 106.4238)
        self.FOREGROUND_COLOR = self._oklch_to_rgb(0.9699, 0.0013, 106.4238)
        
        # Пользователь - серый фон с черным текстом
        # muted: oklch(0.9431 0.0068 53.4442) - светло-серый
        self.USER_BG_COLOR = self._oklch_to_rgb(0.9431, 0.0068, 53.4442)
        self.USER_TEXT_COLOR = self._oklch_to_rgb(0.2178, 0, 0)  # черный
        
        # Ассистент - красный фон с белым текстом
        # primary: oklch(0.58 0.19 25) - красный/оранжевый
        self.ASSISTANT_BG_COLOR = self._oklch_to_rgb(0.58, 0.19, 25)
        self.ASSISTANT_TEXT_COLOR = self._oklch_to_rgb(1.0000, 0, 0)  # белый
        
        # border: oklch(0.9355 0.0324 80.9937)
        self.BORDER_COLOR = self._oklch_to_rgb(0.9355, 0.0324, 80.9937)
        
        # Загрузка шрифтов
        font_loaded = False
        
        # Пытаемся загрузить шрифт в зависимости от ОС
        if platform.system() == "Windows":
            # Windows шрифты
            font_paths = [
                "C:/Windows/Fonts/arial.ttf",
                "C:/Windows/Fonts/calibri.ttf",
                "C:/Windows/Fonts/tahoma.ttf",
            ]
            for font_path in font_paths:
                try:
                    if os.path.exists(font_path):
                        self.font = ImageFont.truetype(font_path, 20)
                        self.bold_font = ImageFont.truetype(font_path, 22)
                        font_loaded = True
                        break
                except:
                    continue
        else:
            # Linux/Mac шрифты
            font_paths = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "/System/Library/Fonts/Helvetica.ttc",  # macOS
            ]
            for font_path in font_paths:
                try:
                    if os.path.exists(font_path):
                        self.font = ImageFont.truetype(font_path, 20)
                        # Пытаемся найти жирный шрифт
                        bold_path = font_path.replace("Regular", "Bold").replace("Sans", "Sans-Bold")
                        if os.path.exists(bold_path):
                            self.bold_font = ImageFont.truetype(bold_path, 22)
                        else:
                            self.bold_font = ImageFont.truetype(font_path, 22)
                        font_loaded = True
                        break
                except:
                    continue
        
        if not font_loaded:
            # Используем шрифт по умолчанию
            self.font = ImageFont.load_default()
            self.bold_font = ImageFont.load_default()
    
    def _get_text_bbox(self, draw: ImageDraw.Draw, text: str, font: ImageFont.FreeTypeFont):
        """Получает размеры текста с учетом версии Pillow"""
        try:
            # Новый метод для Pillow >= 9.0.0
            return draw.textbbox((0, 0), text, font=font)
        except (AttributeError, TypeError):
            # Старый метод для Pillow < 9.0.0
            # textsize возвращает (width, height), преобразуем в bbox формат
            width, height = draw.textsize(text, font=font)
            return (0, 0, width, height)
    
    def _wrap_text(self, draw: ImageDraw.Draw, text: str, max_width: int) -> List[str]:
        """Разбивает текст на строки с учетом ширины в пикселях"""
        lines = []
        for paragraph in text.split('\n'):
            if not paragraph.strip():
                lines.append("")
                continue
            
            # Разбиваем текст по словам
            words = paragraph.split(' ')
            current_line = []
            current_width = 0
            
            for word in words:
                # Проверяем ширину слова
                test_line = ' '.join(current_line + [word])
                bbox = self._get_text_bbox(draw, test_line, self.font)
                word_width = bbox[2] - bbox[0]
                
                if word_width <= max_width:
                    current_line.append(word)
                    current_width = word_width
                else:
                    # Сохраняем текущую строку
                    if current_line:
                        lines.append(' '.join(current_line))
                    # Если одно слово длиннее max_width, разбиваем его
                    if bbox[2] - bbox[0] > max_width:
                        # Пробуем разбить слово
                        char_line = ""
                        for char in word:
                            test_char_line = char_line + char
                            char_bbox = self._get_text_bbox(draw, test_char_line, self.font)
                            if (char_bbox[2] - char_bbox[0]) <= max_width:
                                char_line = test_char_line
                            else:
                                if char_line:
                                    lines.append(char_line)
                                char_line = char
                        if char_line:
                            current_line = [char_line]
                        else:
                            current_line = []
                    else:
                        current_line = [word]
                    current_width = self._get_text_bbox(draw, ' '.join(current_line), self.font)[2] - self._get_text_bbox(draw, ' '.join(current_line), self.font)[0]
            
            if current_line:
                lines.append(' '.join(current_line))
        
        return lines
    
    def _calculate_text_height(self, draw: ImageDraw.Draw, text: str, max_width: int) -> int:
        """Вычисляет высоту текста"""
        lines = self._wrap_text(draw, text, max_width)
        bbox = self._get_text_bbox(draw, "A", self.font)
        line_height = (bbox[3] - bbox[1]) + self.LINE_SPACING
        return len(lines) * line_height
    
    def _draw_rounded_rectangle(
        self,
        draw: ImageDraw.Draw,
        xy: Tuple[int, int, int, int],
        fill: Tuple[int, int, int],
        radius: int
    ):
        """Рисует закругленный прямоугольник"""
        x1, y1, x2, y2 = xy
        
        # Рисуем основной прямоугольник
        draw.rectangle(
            [x1 + radius, y1, x2 - radius, y2],
            fill=fill
        )
        draw.rectangle(
            [x1, y1 + radius, x2, y2 - radius],
            fill=fill
        )
        
        # Рисуем закругленные углы
        draw.ellipse(
            [x1, y1, x1 + radius * 2, y1 + radius * 2],
            fill=fill
        )
        draw.ellipse(
            [x2 - radius * 2, y1, x2, y1 + radius * 2],
            fill=fill
        )
        draw.ellipse(
            [x1, y2 - radius * 2, x1 + radius * 2, y2],
            fill=fill
        )
        draw.ellipse(
            [x2 - radius * 2, y2 - radius * 2, x2, y2],
            fill=fill
        )
    
    def _draw_message(
        self,
        draw: ImageDraw.Draw,
        role: str,
        content: str,
        y_position: int,
        available_width: int,
        username: str = None
    ) -> int:
        """Рисует одно сообщение и возвращает новую позицию Y"""
        # Определяем цвета и позицию в зависимости от роли
        if role == "user":
            bg_color = self.USER_BG_COLOR
            text_color = self.USER_TEXT_COLOR
            label = username or "Пользователь"
            # Сообщение пользователя справа
            message_width = int(available_width * self.MESSAGE_WIDTH_PERCENT)
            x_start = self.IMAGE_WIDTH - self.MARGIN - message_width
            x_end = self.IMAGE_WIDTH - self.MARGIN
        else:
            bg_color = self.ASSISTANT_BG_COLOR
            text_color = self.ASSISTANT_TEXT_COLOR
            label = "Alfa-Helper"
            # Сообщение ассистента слева
            message_width = int(available_width * self.MESSAGE_WIDTH_PERCENT)
            x_start = self.MARGIN
            x_end = self.MARGIN + message_width
        
        # Вычисляем размеры текста
        text_padding = 15
        text_max_width = message_width - text_padding * 2
        text_lines = self._wrap_text(draw, content, text_max_width)
        bbox = self._get_text_bbox(draw, "A", self.font)
        line_height = (bbox[3] - bbox[1]) + self.LINE_SPACING
        
        # Высота метки
        label_bbox = self._get_text_bbox(draw, label, self.bold_font)
        label_height = (label_bbox[3] - label_bbox[1]) + 10
        
        # Высота текста
        text_height = len(text_lines) * line_height
        
        # Общая высота блока сообщения
        block_height = label_height + text_height + text_padding * 2
        
        # Рисуем закругленный фон сообщения
        self._draw_rounded_rectangle(
            draw,
            (x_start, y_position, x_end, y_position + block_height),
            fill=bg_color,
            radius=self.BORDER_RADIUS
        )
        
        # Рисуем метку (роль)
        draw.text(
            (x_start + text_padding, y_position + text_padding),
            label,
            fill=text_color,
            font=self.bold_font
        )
        
        # Рисуем текст сообщения
        current_y = y_position + label_height + text_padding
        for line in text_lines:
            draw.text(
                (x_start + text_padding, current_y),
                line,
                fill=text_color,
                font=self.font
            )
            current_y += line_height
        
        return y_position + block_height + self.MESSAGE_SPACING
    
    def generate_chat_images(self, messages: List[Dict[str, str]], username: str = None) -> List[BytesIO]:
        """
        Генерирует изображения истории чата
        
        Args:
            messages: Список сообщений в формате [{"role": "user"/"assistant", "content": "текст"}]
            username: Имя пользователя для отображения в сообщениях
        
        Returns:
            Список BytesIO объектов с изображениями
        """
        if not messages:
            return []
        
        images = []
        current_messages = []
        available_width = self.IMAGE_WIDTH - 2 * self.MARGIN
        message_width = int(available_width * self.MESSAGE_WIDTH_PERCENT)
        max_text_width = message_width - 30  # padding * 2
        
        # Создаем временное изображение для расчета размеров
        temp_img = Image.new('RGB', (self.IMAGE_WIDTH, 100), self.BG_COLOR)
        temp_draw = ImageDraw.Draw(temp_img)
        
        current_height = self.MARGIN + 40  # Заголовок
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            # Вычисляем высоту сообщения
            message_height = self._calculate_text_height(temp_draw, content, max_text_width)
            # Используем максимальную ширину метки для расчета
            label_text = username or "Пользователь" if role == "user" else "Alfa-Helper"
            label_bbox = self._get_text_bbox(temp_draw, label_text, self.bold_font)
            label_height = (label_bbox[3] - label_bbox[1]) + 10
            total_message_height = label_height + message_height + 30 + self.MESSAGE_SPACING  # padding * 2
            
            # Проверяем, поместится ли сообщение на текущее изображение
            if current_height + total_message_height > self.MAX_HEIGHT and current_messages:
                # Создаем изображение с текущими сообщениями
                img = self._create_image(current_messages, username)
                images.append(img)
                
                # Начинаем новое изображение
                current_messages = [message]
                current_height = self.MARGIN + 40 + total_message_height
            else:
                current_messages.append(message)
                current_height += total_message_height
        
        # Создаем последнее изображение, если есть сообщения
        if current_messages:
            img = self._create_image(current_messages, username)
            images.append(img)
        
        return images
    
    def _create_image(self, messages: List[Dict[str, str]], username: str = None) -> BytesIO:
        """Создает одно изображение с сообщениями"""
        # Вычисляем общую высоту
        available_width = self.IMAGE_WIDTH - 2 * self.MARGIN
        message_width = int(available_width * self.MESSAGE_WIDTH_PERCENT)
        max_text_width = message_width - 30  # padding * 2
        
        # Создаем временное изображение для расчета размеров
        temp_img = Image.new('RGB', (self.IMAGE_WIDTH, 100), self.BG_COLOR)
        temp_draw = ImageDraw.Draw(temp_img)
        
        total_height = self.MARGIN + 40  # Заголовок
        
        for message in messages:
            content = message.get("content", "")
            role = message.get("role", "user")
            message_height = self._calculate_text_height(temp_draw, content, max_text_width)
            # Используем максимальную ширину метки для расчета
            label_text = username or "Пользователь" if role == "user" else "Alfa-Helper"
            label_bbox = self._get_text_bbox(temp_draw, label_text, self.bold_font)
            label_height = (label_bbox[3] - label_bbox[1]) + 10
            total_height += label_height + message_height + 30 + self.MESSAGE_SPACING  # padding * 2
        
        total_height += self.MARGIN
        
        # Создаем изображение
        img = Image.new('RGB', (self.IMAGE_WIDTH, total_height), self.BG_COLOR)
        draw = ImageDraw.Draw(img)
        
        # Рисуем заголовок
        title = "История диалога"
        title_bbox = self._get_text_bbox(draw, title, self.bold_font)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(
            ((self.IMAGE_WIDTH - title_width) // 2, self.MARGIN // 2),
            title,
            fill=self.FOREGROUND_COLOR,
            font=self.bold_font
        )
        
        # Рисуем сообщения
        y_pos = self.MARGIN + 40
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            y_pos = self._draw_message(draw, role, content, y_pos, available_width, username)
        
        # Сохраняем в BytesIO
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return img_bytes


# Глобальный экземпляр сервиса
chat_image_service = ChatImageService()

