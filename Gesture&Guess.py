import pygame
import sys
import random
import os
import math
import json
import pygame.freetype
import sys
import os

def resource_path(relative_path):
    try:
        # PyInstaller 创建临时文件夹存储路径
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# 初始化pygame
pygame.init()
pygame.mixer.init()

# 默认设置
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
FULLSCREEN = False
if FULLSCREEN:
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
else:
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("茶话会你划我猜")

# 颜色定义
BACKGROUND = (25, 25, 40)
TITLE_COLOR = (220, 180, 255)
BUTTON_COLOR = (70, 60, 110)
BUTTON_HOVER = (100, 80, 160)
BUTTON_TEXT = (230, 230, 250)
SETTINGS_BG = (35, 35, 55)
SETTINGS_PANEL = (45, 40, 80)
TEXT_COLOR = (220, 220, 250)
HIGHLIGHT = (255, 200, 100)
TIMER_COLOR = (255, 150, 100)
GAME_BG = (30, 30, 45)

# 加载音效
try:
    button_sound = pygame.mixer.Sound(resource_path("button.wav"))
    gameover_sound = pygame.mixer.Sound(resource_path("gameover.wav"))
    gamestart_sound = pygame.mixer.Sound(resource_path("gamestart.wav"))
    getpoint_sound = pygame.mixer.Sound(resource_path("getpoint.wav"))
    losepoint_sound = pygame.mixer.Sound(resource_path("losepoint.wav"))
except:
    print("警告：部分音效文件缺失，游戏将在无音效模式下运行")
    button_sound = None
    gameover_sound = None
    getpoint_sound = None
    losepoint_sound = None
    gamestart_sound = None


def load_font(size, bold=False):
    font_path = resource_path("HYPixel11pxU-2.ttf")

    try:
        if os.path.exists(font_path):
            font = pygame.freetype.Font(font_path, size)
            if bold:
                font.bold = True
            return font
        else:
            raise FileNotFoundError(f"字体文件 {font_path} 不存在！")

    except Exception as e:
        print(f"字体加载错误: {e}")
        # 失败则退回系统默认字体
        return pygame.freetype.SysFont(None, size)


# 创建字体
title_font = load_font(80)
button_font = load_font(36)
small_font = load_font(28)
timer_font = load_font(40)
game_font = load_font(48)
countdown_font = load_font(120)


# 游戏状态
class GameState:
    TITLE = 0
    SETTINGS = 1
    GAME = 2
    COUNTDOWN = 3  # 新增倒计时状态
    GAME_OVER = 4


# 游戏设置
class GameSettings:
    def __init__(self):
        self.resolution = "1080p"
        self.volume = 0.7
        self.time_limit = 60  # 默认60秒
        self.resolutions = {
            "720p": (1280, 720),
            "1080p": (1920, 1080),
            "4k": (3840, 2160)
        }
        self.time_options = [30, 60, 300, 0]  # 0表示无限制
        self.time_labels = ["30秒", "1分钟", "5分钟", "无限制"]

    def get_resolution(self):
        return self.resolutions[self.resolution]


# 创建游戏设置实例
settings = GameSettings()


# 加载题目
def load_questions():
    # 从topics.json加载题目
    try:
        with open(resource_path('topics.json'), 'r', encoding='utf-8') as f:
            topics = json.load(f)
        return topics
    except Exception as e:
        print(f"加载题目失败: {e}")
        # 默认题目
        return [
            {"type": "image", "path": "/pictures/xiapila.png"},
            {"type": "image", "path": "/pictures/xiapila2.png"},
            {"type": "image", "path": "/pictures/xintila.png"},
            {"type": "image", "path": "/pictures/xiutaerke.png"},
            {"type": "image", "path": "/pictures/xiya.png"},
            {"type": "image", "path": "/pictures/yala.png"},
            {"type": "image", "path": "/pictures/yinhe.png"},
            {"type": "image", "path": "/pictures/yiwa.png"},
            {"type": "image", "path": "/pictures/yiwa2.png"},
            {"type": "image", "path": "/pictures/youjin.png"},
            {"type": "image", "path": "/pictures/youzi.png"},
            {"type": "image", "path": "/pictures/youzi2.png"},
            {"type": "image", "path": "/pictures/yun.png"},
            {"type": "image", "path": "/pictures/yuna.png"},
            {"type": "image", "path": "/pictures/yunling.png"},
            {"type": "image", "path": "/pictures/zao.png"},
            {"type": "image", "path": "/pictures/zhucai.png"}
        ]


# 按钮类
class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hovered = False
        self.radius = 15

    def draw(self, surface):
        color = BUTTON_HOVER if self.hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=self.radius)
        pygame.draw.rect(surface, (150, 140, 180), self.rect, 3, border_radius=self.radius)

        text_surf, text_rect = button_font.render(self.text, BUTTON_TEXT)
        text_rect.center = self.rect.center
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if button_sound:
                    button_sound.play()
                if self.action:
                    return self.action()
        return None


# 滑块类
class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, label):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.label = label
        self.dragging = False
        self.knob_radius = 15
        self.knob_x = x + (initial_val - min_val) / (max_val - min_val) * width

    def draw(self, surface):
        # 绘制滑块轨道
        pygame.draw.rect(surface, (60, 55, 85), self.rect, border_radius=7)
        pygame.draw.rect(surface, (100, 90, 150),
                         (self.rect.x, self.rect.y, self.knob_x - self.rect.x, self.rect.height),
                         border_radius=7)

        # 绘制滑块旋钮
        pygame.draw.circle(surface, BUTTON_HOVER, (int(self.knob_x), self.rect.centery), self.knob_radius)
        pygame.draw.circle(surface, (180, 170, 210), (int(self.knob_x), self.rect.centery), self.knob_radius, 2)

        # 绘制标签和值
        label_surf, _ = small_font.render(f"{self.label}: {int(self.value * 100)}%", TEXT_COLOR)
        surface.blit(label_surf, (self.rect.x, self.rect.y - 30))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            knob_rect = pygame.Rect(self.knob_x - self.knob_radius, self.rect.centery - self.knob_radius,
                                    self.knob_radius * 2, self.knob_radius * 2)
            if knob_rect.collidepoint(event.pos):
                self.dragging = True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.knob_x = max(self.rect.x, min(event.pos[0], self.rect.x + self.rect.width))
            self.value = self.min_val + (self.knob_x - self.rect.x) / self.rect.width * (self.max_val - self.min_val)
            return True

        return False


# 选择器类
class Selector:
    def __init__(self, x, y, width, height, options, labels, initial_index, label):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.labels = labels
        self.index = initial_index
        self.label = label
        self.button_width = width // len(options)

    def draw(self, surface):
        # 绘制标签
        label_surf, _ = small_font.render(self.label, TEXT_COLOR)
        surface.blit(label_surf, (self.rect.x, self.rect.y - 30))

        # 绘制选项按钮
        for i, option in enumerate(self.options):
            option_rect = pygame.Rect(self.rect.x + i * self.button_width, self.rect.y,
                                      self.button_width, self.rect.height)

            color = BUTTON_HOVER if i == self.index else BUTTON_COLOR
            pygame.draw.rect(surface, color, option_rect, border_radius=10)
            pygame.draw.rect(surface, (150, 140, 180), option_rect, 2, border_radius=10)

            # 使用预定义的标签文本
            text = self.labels[i]
            text_surf, text_rect = small_font.render(text, BUTTON_TEXT)
            text_rect.center = option_rect.center
            surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i in range(len(self.options)):
                option_rect = pygame.Rect(self.rect.x + i * self.button_width, self.rect.y,
                                          self.button_width, self.rect.height)
                if option_rect.collidepoint(event.pos):
                    self.index = i
                    if button_sound:
                        button_sound.play()
                    return True
        return False


# 游戏主类
class GestureGuessGame:
    def __init__(self):
        self.timer_expired = False
        self.state = GameState.TITLE
        self.clock = pygame.time.Clock()
        self.settings = settings
        self.questions = load_questions()  # 加载题目
        self.current_question = None
        self.time_left = 0
        self.game_start_time = 0
        self.score = 0
        self.round_count = 0
        self.fullscreen = FULLSCREEN
        self.countdown_value = 3  # 3秒倒计时
        self.countdown_start = 0
        self.scale_factor = 1.0  # 新增缩放因子

        self.load_background()  # 加载背景

        # 创建UI元素
        self.create_title_ui()
        self.create_settings_ui()
        self.create_game_ui()

    def load_background(self):
        try:
            raw_bg = pygame.image.load(resource_path("bg.jpg")).convert()

            # 计算缩放比例，保持宽高比
            img_width, img_height = raw_bg.get_size()
            screen_ratio = SCREEN_WIDTH / SCREEN_HEIGHT
            img_ratio = img_width / img_height

            if img_ratio < screen_ratio:
                # 图片偏高，宽度适配屏幕，裁剪上下
                new_width = SCREEN_WIDTH
                new_height = int(SCREEN_WIDTH / img_ratio)
            else:
                # 图片偏宽，高度适配屏幕，裁剪左右
                new_height = SCREEN_HEIGHT
                new_width = int(SCREEN_HEIGHT * img_ratio)

            # 等比缩放
            scaled_bg = pygame.transform.smoothscale(raw_bg, (new_width, new_height))

            # 计算偏移用于裁剪中间部分（中心居中）
            offset_x = (new_width - SCREEN_WIDTH) // 2
            offset_y = (new_height - SCREEN_HEIGHT) // 2

            # 裁剪屏幕区域
            self.title_bg = scaled_bg.subsurface(pygame.Rect(offset_x, offset_y, SCREEN_WIDTH, SCREEN_HEIGHT)).copy()

            print(f"背景已重新加载: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
        except Exception as e:
            print(f"无法加载标题背景图片: {e}")
            self.title_bg = None

    def toggle_fullscreen(self):
        global screen, SCREEN_WIDTH, SCREEN_HEIGHT, FULLSCREEN
        self.fullscreen = not self.fullscreen
        FULLSCREEN = self.fullscreen

        if self.fullscreen:
            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
            self.fullscreen_button.text = "窗口模式"
            # 计算缩放因子 - 基于屏幕高度相对于720p的比例
            self.scale_factor = SCREEN_HEIGHT / 720.0
        else:
            screen = pygame.display.set_mode((1280, 720))
            SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
            self.fullscreen_button.text = "全屏模式"
            self.scale_factor = 1.0

        # 重新创建UI
        self.create_title_ui()
        self.create_settings_ui()
        self.create_game_ui()
        self.load_background()  # 重新加载背景以适应新尺寸
        return True

    def create_title_ui(self):
        button_width, button_height = int(300 * self.scale_factor), int(70 * self.scale_factor)
        center_x = SCREEN_WIDTH // 2

        self.title_buttons = [
            Button(center_x - button_width // 2, int(350 * self.scale_factor), button_width, button_height, "开始游戏",
                   self.start_game),
            Button(center_x - button_width // 2, int(450 * self.scale_factor), button_width, button_height, "游戏设置",
                   self.open_settings),
            Button(center_x - button_width // 2, int(550 * self.scale_factor), button_width, button_height, "退出游戏",
                   self.quit_game)
        ]

    def create_settings_ui(self):
        center_x = SCREEN_WIDTH // 2
        panel_width, panel_height = int(600 * self.scale_factor), int(450 * self.scale_factor)

        # 设置界面上移
        self.settings_panel = pygame.Rect(center_x - panel_width // 2, int(150 * self.scale_factor), panel_width,
                                          panel_height)

        # 分辨率选择器
        resolution_options = list(settings.resolutions.keys())
        resolution_labels = resolution_options
        self.resolution_selector = Selector(
            center_x - int(250 * self.scale_factor), int(230 * self.scale_factor),
            int(500 * self.scale_factor), int(60 * self.scale_factor),
            resolution_options, resolution_labels,
            list(settings.resolutions.keys()).index(settings.resolution),
            "分辨率"
        )

        # 音量滑块
        min_val = 0.0
        max_val = 1.0
        self.volume_slider = Slider(
            center_x - int(250 * self.scale_factor), int(330 * self.scale_factor),
            int(500 * self.scale_factor), int(20 * self.scale_factor),
            min_val, max_val, settings.volume, "音量"
        )

        # 时间限制选择器
        time_options = settings.time_options
        time_labels = settings.time_labels
        time_index = settings.time_options.index(settings.time_limit)
        self.time_selector = Selector(
            center_x - int(250 * self.scale_factor), int(430 * self.scale_factor),
            int(500 * self.scale_factor), int(60 * self.scale_factor),
            time_options, time_labels, time_index, "时间限制"
        )

        # 全屏按钮
        self.fullscreen_button = Button(center_x - int(250 * self.scale_factor), int(500 * self.scale_factor),
                                        int(200 * self.scale_factor), int(60 * self.scale_factor),
                                        "全屏模式" if not self.fullscreen else "窗口模式",
                                        self.toggle_fullscreen)

        # 返回按钮
        self.back_button = Button(center_x - int(100 * self.scale_factor), int(580 * self.scale_factor),
                                  int(200 * self.scale_factor), int(60 * self.scale_factor),
                                  "返回", self.return_to_title)

    def create_game_ui(self):
        # 计算缩放后的尺寸
        button_width = int(180 * self.scale_factor)
        button_height = int(60 * self.scale_factor)

        self.next_button = Button(
            SCREEN_WIDTH - button_width - int(50 * self.scale_factor),
            SCREEN_HEIGHT - button_height - int(50 * self.scale_factor),
            button_width, button_height, "下一题", self.next_question
        )

        self.return_button = Button(
            int(50 * self.scale_factor),
            SCREEN_HEIGHT - button_height - int(50 * self.scale_factor),
            button_width, button_height, "返回标题", self.return_to_title
        )

        # 计时器和题目区域 - 根据屏幕尺寸动态调整
        timer_width = int(200 * self.scale_factor)
        timer_height = int(60 * self.scale_factor)
        self.timer_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - timer_width // 2,
            int(150 * self.scale_factor),
            timer_width, timer_height
        )

        # 题目区域 - 根据屏幕尺寸动态调整大小
        question_width = int(600 * self.scale_factor)
        question_height = int(300 * self.scale_factor)
        self.question_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - question_width // 2,
            int(250 * self.scale_factor),
            question_width, question_height
        )

    def apply_settings(self):
        # 应用分辨率设置
        new_res = self.resolution_selector.options[self.resolution_selector.index]
        if new_res != self.settings.resolution:
            self.settings.resolution = new_res
            width, height = self.settings.get_resolution()
            global SCREEN_WIDTH, SCREEN_HEIGHT, screen
            SCREEN_WIDTH, SCREEN_HEIGHT = width, height

            if self.fullscreen:
                screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
                self.scale_factor = SCREEN_HEIGHT / 720.0
            else:
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                self.scale_factor = 1.0

            # 重新创建UI
            self.create_title_ui()
            self.create_settings_ui()
            self.create_game_ui()
            self.load_background()  # 重新加载背景以适应新分辨率

        # 应用音量设置
        self.settings.volume = self.volume_slider.value

        # 应用时间限制设置
        self.settings.time_limit = self.time_selector.options[self.time_selector.index]

    def start_game(self):
        self.state = GameState.COUNTDOWN  # 先进入倒计时状态
        self.countdown_value = 3
        self.countdown_start = pygame.time.get_ticks()
        self.score = 0
        self.round_count = 0
        return True

    def start_game_after_countdown(self):
        self.state = GameState.GAME
        self.next_question()

    def next_question(self):
        self.current_question = random.choice(self.questions)
        self.time_left = self.settings.time_limit
        self.game_start_time = pygame.time.get_ticks()
        self.round_count += 1

        # 如果当前题目是图片，则加载图片
        if self.current_question["type"] == "image":
            # 在绘制时加载
            if "surface" in self.current_question:
                del self.current_question["surface"]

    def open_settings(self):
        self.state = GameState.SETTINGS
        return True

    def return_to_title(self):
        self.state = GameState.TITLE
        return True

    def quit_game(self):
        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()

            # 标题界面事件处理
            if self.state == GameState.TITLE:
                mouse_pos = pygame.mouse.get_pos()
                for button in self.title_buttons:
                    button.check_hover(mouse_pos)
                    action = button.handle_event(event)
                    if action:
                        return

            # 设置界面事件处理
            elif self.state == GameState.SETTINGS:
                mouse_pos = pygame.mouse.get_pos()

                # 处理滑块
                if self.volume_slider.handle_event(event):
                    pass

                # 处理选择器
                if self.resolution_selector.handle_event(event):
                    pass

                if self.time_selector.handle_event(event):
                    pass

                # 处理全屏按钮
                self.fullscreen_button.check_hover(mouse_pos)
                if self.fullscreen_button.handle_event(event):
                    pass

                # 处理返回按钮
                self.back_button.check_hover(mouse_pos)
                action = self.back_button.handle_event(event)
                if action:
                    self.apply_settings()
                    return

            # 游戏界面事件处理
            elif self.state == GameState.GAME:
                mouse_pos = pygame.mouse.get_pos()

                self.next_button.check_hover(mouse_pos)
                next_action = self.next_button.handle_event(event)
                if next_action:
                    return

                self.return_button.check_hover(mouse_pos)
                return_action = self.return_button.handle_event(event)
                if return_action:
                    return

            # 倒计时状态事件处理
            elif self.state == GameState.COUNTDOWN:
                pass

            # 通用按键处理
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.SETTINGS or self.state == GameState.GAME:
                        self.return_to_title()
                    elif self.state == GameState.TITLE:
                        self.quit_game()
                elif event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                elif event.key == pygame.K_UP:
                    self.score += 1
                    if getpoint_sound:
                        getpoint_sound.play()
                elif event.key == pygame.K_DOWN:
                    self.score = max(0, self.score - 1)
                    if losepoint_sound:
                        losepoint_sound.play()

    def update(self):
        # 更新游戏逻辑
        if self.state == GameState.GAME:
            # 更新时间
            if self.settings.time_limit > 0:
                elapsed = (pygame.time.get_ticks() - self.game_start_time) // 1000
                previous_time_left = self.time_left
                self.time_left = max(0, self.settings.time_limit - elapsed)

                # 判断是否刚刚到时间 0
                if self.time_left == 0 and previous_time_left > 0:
                    self.timer_expired = True  # 刚刚变成 0

                # 播放音效（只一次）
                if self.timer_expired and gameover_sound:
                    gameover_sound.play()
                    self.timer_expired = False  # 播放后清除标记

        # 倒计时状态更新
        elif self.state == GameState.COUNTDOWN:
            elapsed = (pygame.time.get_ticks() - self.countdown_start) // 1000
            self.countdown_value = max(0, 3 - elapsed)

            # 倒计时结束
            if self.countdown_value == 0:
                self.start_game_after_countdown()

    def draw_title_screen(self):
        # 绘制背景
        screen.fill(BACKGROUND)

        # 如果有背景图片，使用叠加模式绘制
        if self.title_bg:
            # 创建临时surface用于叠加
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))  # 半透明黑色覆盖层

            # 绘制背景图片
            screen.blit(self.title_bg, (0, 0))
            # 绘制覆盖层
            screen.blit(overlay, (0, 0))

        # 绘制装饰粒子
        for i in range(100):
            x = (i * 37) % SCREEN_WIDTH
            y = (i * 23) % SCREEN_HEIGHT
            size = 1 + (i % 3)
            alpha = 50 + (i % 100)
            color = (150, 120, 200, alpha)
            pygame.draw.circle(screen, color, (x, y), size)

        # 绘制标题
        title_surf, title_rect = title_font.render("茶话会你划我猜", TITLE_COLOR)
        title_rect.center = (SCREEN_WIDTH // 2, int(180 * self.scale_factor))
        screen.blit(title_surf, title_rect)

        # 绘制副标题
        subtitle, subtitle_rect = small_font.render("用动作表达题目，让伙伴猜出答案", (180, 160, 220))
        subtitle_rect.center = (SCREEN_WIDTH // 2, int(260 * self.scale_factor))
        screen.blit(subtitle, subtitle_rect)

        # 绘制按钮
        for button in self.title_buttons:
            button.draw(screen)

        # 绘制底部信息
        footer, _ = small_font.render("按ESC键退出游戏 | F11切换全屏", (120, 110, 150))
        screen.blit(footer, (SCREEN_WIDTH - footer.get_width() - 20, SCREEN_HEIGHT - 40))

    def draw_settings_screen(self):
        # 绘制背景
        screen.fill(BACKGROUND)

        # 绘制设置面板
        pygame.draw.rect(screen, SETTINGS_PANEL, self.settings_panel, border_radius=20)
        pygame.draw.rect(screen, (90, 80, 130), self.settings_panel, 4, border_radius=20)

        # 绘制设置标题
        settings_title, title_rect = title_font.render("游戏设置", TITLE_COLOR)
        title_rect.center = (SCREEN_WIDTH // 2, int(100 * self.scale_factor))
        screen.blit(settings_title, title_rect)

        # 绘制设置项
        self.resolution_selector.draw(screen)
        self.volume_slider.draw(screen)
        self.time_selector.draw(screen)

        # 绘制全屏按钮
        self.fullscreen_button.draw(screen)

        # 绘制返回按钮
        self.back_button.draw(screen)

        # 绘制提示
        hint, _ = small_font.render("更改分辨率将在返回标题后生效", (180, 160, 220))
        screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 50))

    def draw_countdown_screen(self):
        # 绘制背景
        screen.fill(GAME_BG)

        # 绘制倒计时数字
        countdown_text = str(self.countdown_value) if self.countdown_value > 0 else "开始!"
        color = (255, 200, 100) if self.countdown_value > 0 else (100, 255, 100)
        countdown_surf, countdown_rect = countdown_font.render(countdown_text, color)
        countdown_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        screen.blit(countdown_surf, countdown_rect)

        # 绘制提示
        hint, _ = small_font.render("准备开始游戏...", (180, 180, 220))
        screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 100))

        # 播放游戏开始音效：在 countdown_value == 3 时延迟 0.2 秒播放一次
        if self.countdown_value == 3:
            if not hasattr(self, 'countdown_sound_timer_started') or not self.countdown_sound_timer_started:
                self.countdown_sound_timer_started = True
                self.countdown_sound_start_time = pygame.time.get_ticks()
                self.gamestart_played = False  # 重置音效播放标志

            elif not self.gamestart_played:
                elapsed = pygame.time.get_ticks() - self.countdown_sound_start_time
                if elapsed >= 80:  # 0.08秒延迟
                    if gamestart_sound:
                        gamestart_sound.play()
                    self.gamestart_played = True

        else:
            # 一旦倒计时值不是3，就重置标志，方便下次重新倒计时时再播放一次
            self.countdown_sound_timer_started = False
            self.gamestart_played = False

    def draw_game_screen(self):
        # 绘制背景
        screen.fill(GAME_BG)

        # 绘制装饰边框
        border_size = int(20 * self.scale_factor)
        pygame.draw.rect(screen, (50, 45, 75),
                         (border_size, border_size,
                          SCREEN_WIDTH - 2 * border_size,
                          SCREEN_HEIGHT - 2 * border_size),
                         5, border_radius=int(10 * self.scale_factor))

        # 绘制标题（字体大小根据缩放因子调整）
        title_size = int(48 * self.scale_factor)
        game_title_font = load_font(title_size)
        title_surf, title_rect = game_title_font.render("你划我猜", TITLE_COLOR)
        title_rect.center = (SCREEN_WIDTH // 2, int(70 * self.scale_factor))
        screen.blit(title_surf, title_rect)

        # 绘制分数和回合
        score_size = int(36 * self.scale_factor)
        score_font = load_font(score_size)
        score_text, _ = score_font.render(f"分数: {self.score}", HIGHLIGHT)
        screen.blit(score_text, (int(50 * self.scale_factor), int(50 * self.scale_factor)))

        round_text, _ = score_font.render(f"回合: {self.round_count}", HIGHLIGHT)
        screen.blit(round_text, (SCREEN_WIDTH - round_text.get_width() - int(50 * self.scale_factor),
                                 int(50 * self.scale_factor)))

        # 绘制计时器（位置下移）
        pygame.draw.rect(screen, (50, 45, 75), self.timer_rect, border_radius=int(15 * self.scale_factor))
        pygame.draw.rect(screen, (100, 90, 150), self.timer_rect, 3, border_radius=int(15 * self.scale_factor))

        if self.settings.time_limit > 0:
            timer_text = f"{self.time_left // 60}:{self.time_left % 60:02d}"
        else:
            timer_text = "无限制"

        timer_size = int(40 * self.scale_factor)
        timer_font_scaled = load_font(timer_size)
        timer_surf, timer_rect = timer_font_scaled.render(timer_text, TIMER_COLOR)
        timer_rect.center = self.timer_rect.center
        screen.blit(timer_surf, timer_rect)

        # 时间结束显示"挑战失败"
        if self.settings.time_limit > 0 and self.time_left == 0:
            fail_size = int(48 * self.scale_factor)
            fail_font = load_font(fail_size)
            fail_surf, fail_rect = fail_font.render("挑战失败!", (255, 50, 50))
            fail_rect.center = (SCREEN_WIDTH // 2, self.question_rect.bottom + int(50 * self.scale_factor))
            screen.blit(fail_surf, fail_rect)

            # 播放游戏结束音效（只播放一次）
            if gameover_sound and self.timer_expired:
                gameover_sound.play()
                self.timer_expired = False  # 播放完毕后关闭开关
        # 绘制题目区域（位置下移）
        pygame.draw.rect(screen, (40, 35, 65), self.question_rect, border_radius=int(20 * self.scale_factor))
        pygame.draw.rect(screen, (90, 80, 130), self.question_rect, 4, border_radius=int(20 * self.scale_factor))

        # 绘制题目（从topics.json加载）
        if self.current_question:
            if self.current_question["type"] == "text":
                # 显示文字题目 - 使用缩放后的字体
                text_size = int(48 * self.scale_factor)
                text_font = load_font(text_size)
                text_surf, text_rect = text_font.render(self.current_question["content"], HIGHLIGHT)
                text_rect.center = self.question_rect.center
                screen.blit(text_surf, text_rect)
            else:  # 图片题目
                try:
                    # 加载图片（如果还没有加载）
                    if "surface" not in self.current_question:
                        img_path = self.current_question["path"]
                        # 如果路径以/开头，去掉开头的/
                        if img_path.startswith("/"):
                            img_path = img_path[1:]
                        # 加载图片
                        image = pygame.image.load(img_path)

                        # 按比例缩放图片（保持原始比例）
                        img_width, img_height = image.get_size()
                        max_width = self.question_rect.width - int(40 * self.scale_factor)
                        max_height = self.question_rect.height - int(40 * self.scale_factor)

                        # 计算缩放比例
                        width_ratio = max_width / img_width
                        height_ratio = max_height / img_height
                        scale_ratio = min(width_ratio, height_ratio)

                        # 缩放图片
                        new_width = int(img_width * scale_ratio)
                        new_height = int(img_height * scale_ratio)
                        image = pygame.transform.scale(image, (new_width, new_height))

                        self.current_question["surface"] = image
                        self.current_question["rect"] = image.get_rect(center=self.question_rect.center)

                    # 显示图片
                    screen.blit(self.current_question["surface"], self.current_question["rect"])
                except Exception as e:
                    print(f"加载图片失败: {e}")
                    error_size = int(28 * self.scale_factor)
                    error_font = load_font(error_size)
                    error_surf, error_rect = error_font.render("图片加载失败", HIGHLIGHT)
                    error_rect.center = self.question_rect.center
                    screen.blit(error_surf, error_rect)

        # 绘制按钮
        self.next_button.draw(screen)
        self.return_button.draw(screen)

        # 绘制提示（位置上移并修改内容）
        hint_size = int(28 * self.scale_factor)
        hint_font = load_font(hint_size)
        hint, _ = hint_font.render("按↑键增加分数 | 按↓键减少分数 | F11切换全屏", (120, 110, 150))
        screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2,
                           SCREEN_HEIGHT - int(80 * self.scale_factor)))

    def draw(self):
        if self.state == GameState.TITLE:
            self.draw_title_screen()
        elif self.state == GameState.SETTINGS:
            self.draw_settings_screen()
        elif self.state == GameState.GAME:
            self.draw_game_screen()
        elif self.state == GameState.COUNTDOWN:
            self.draw_countdown_screen()

        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)


# 运行游戏
if __name__ == "__main__":
    game = GestureGuessGame()
    game.run()