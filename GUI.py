import pygame
from pygame import Color as pgClr

import os

from typing import Union, Optional, Callable

pygame.init()
mouse_in_use = False


def do_nothing():
    pass


def update_mouse():
    global mouse_in_use
    if not pygame.mouse.get_pressed()[0]:
        mouse_in_use = False


class Label:
    def __init__(
        self, position: Union[tuple[float, float], list[float, float]],
        text: str = "",
        font: pygame.font.Font = pygame.font.Font("freesansbold.ttf", 20),
        foreground: Union[str, pgClr] = "#000000",
        background: Union[str, pgClr, None] = None
    ):
        self.position = position
        self.text = text
        self.foreground = foreground
        self.background = background
        self.font = font

    def draw(self, screen: pygame.Surface):
        text = self.font.render(self.text, True, self.foreground)
        text_rect = text.get_rect()
        text_rect.midleft = self.position

        if self.background:
            pygame.draw.rect(screen, self.background, text_rect)

        screen.blit(text, text_rect)


class TextInput:
    def __init__(
        self, position: Union[tuple[float, float], list[float, float]],
        length: float = 175,
        font: pygame.font.Font = pygame.font.Font("freesansbold.ttf", 20),
        background: Union[str, pgClr] = "#e7e7e7",
        foreground: Union[str, pgClr] = "#000000",
        border_color: Union[str, pgClr] = "#000000",
        border_width: int = 1,
        border_radius: int = 4,
        padding: float = 2
    ):
        self.font = font

        self.position = position

        self.width = length
        self.height = self.font.get_height() * 1.5
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.surface_rect = self.surface.get_rect()
        self.surface_rect.center = self.position

        self.background = background
        self.foreground = foreground
        self.border_color = border_color
        self.border_width = border_width
        self.border_radius = border_radius
        self.padding = padding

        self.text = ""

        self.invalid_chars = []

        self.is_active = False
        self.cursor_position = 0

    def draw(self, screen: pygame.Surface):
        screen.blit(self.surface, self.surface_rect)

    def update(self, mouse_position: tuple[float, float], event: pygame.event.Event):
        global mouse_in_use

        pygame.draw.rect(self.surface, self.background, pygame.Rect(0, 0, self.width, self.height), 0,
                         self.border_radius)
        pygame.draw.rect(self.surface, self.border_color, pygame.Rect(0, 0, self.width, self.height),
                         self.border_width, self.border_radius)

        if self.surface_rect.collidepoint(mouse_position) and not mouse_in_use:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
            if pygame.mouse.get_pressed()[0]:
                self.is_active = True
                self.cursor_position = len(self.text)
                mouse_in_use = True
        if not self.surface_rect.collidepoint(mouse_position):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            if pygame.mouse.get_pressed()[0]:
                self.is_active = False
                mouse_in_use = True

        txt = self.font.render(self.text, True, self.foreground)
        txt_rect = txt.get_rect()
        txt_rect.midleft = (self.padding, self.height / 2)

        if self.is_active:
            if event.type == pygame.KEYDOWN:
                if event.unicode not in ['\b', '\t', '\x7f', '\x08', '\r', '\x1b', ""] + self.invalid_chars:
                    self.text = self.text[:self.cursor_position] + event.unicode + self.text[self.cursor_position:]
                    self.cursor_position += 1

                if event.key == pygame.K_LEFT:
                    if self.cursor_position != 0:
                        self.cursor_position -= 1
                if event.key == pygame.K_RIGHT:
                    if self.cursor_position != len(self.text):
                        self.cursor_position += 1

                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:self.cursor_position - 1] + self.text[self.cursor_position:]
                    if self.cursor_position != 0:
                        self.cursor_position -= 1
                if event.key == pygame.K_DELETE:
                    self.text = self.text[:self.cursor_position] + self.text[self.cursor_position + 1:]
                if event.key == pygame.K_RETURN:
                    self.is_active = False

            pygame.draw.rect(
                self.surface, self.border_color, pygame.Rect(0, 0, self.width, self.height), self.border_width + 1,
                4
            )
            x = self.font.render(self.text[:self.cursor_position], True, "#000000").get_rect().width + 3
            x_ = x
            if x > self.width:
                txt = self.font.render(self.text[:self.cursor_position], True, self.foreground)
                txt_rect = txt.get_rect()
                txt_rect.midright = (self.width - 3 - self.padding, self.height / 2)
                x_ = self.width - 3 - self.padding
            pygame.draw.line(self.surface, "#000000", (x_, self.height / 7), (x_, 6 * self.height / 7), 1)

        self.surface.blit(txt, txt_rect)


class Button:
    def __init__(
        self, size: Union[tuple[float, float], list[float, float]],
        position: Union[tuple[float, float], list[float, float]],
        image: Optional[pygame.Surface] = None,
        text: Optional[str] = None,
        font: Optional[pygame.font.Font] = None,

        background: Union[
            tuple[str, str, str, str], list[str, str, str, str],
            tuple[pgClr, pgClr, pgClr, pgClr], list[pgClr, pgClr, pgClr, pgClr]
        ] = ("#efefef", "#e5e5e5", "#f5f5f5", "#f7f7f7"),

        foreground: Union[
            tuple[str, str, str, str], list[str, str, str, str],
            tuple[pgClr, pgClr, pgClr, pgClr], list[pgClr, pgClr, pgClr, pgClr]
        ] = ("#000000", "#000000", "#000000", "#383838"),

        border_color: Union[
            tuple[str, str, str, str], list[str, str, str, str],
            tuple[pgClr, pgClr, pgClr, pgClr], list[pgClr, pgClr, pgClr, pgClr]
        ] = ("#000000", "#000000", "#000000", "#383838"),

        border_width: int = 1,
        border_radius: int = 4,
        disabled: bool = False,
        command: Callable = do_nothing
    ):
        self.surface = pygame.Surface(size, pygame.SRCALPHA)
        self.surface_rect = self.surface.get_rect()
        self.surface_rect.center = position
        self.rect = pygame.Rect(0, 0, size[0], size[1])
        self.background = list(background)
        self.foreground = list(foreground)
        self.border_color = list(border_color)

        self.border_width = border_width
        self.border_radius = border_radius

        self.image = pygame.Surface((0, 0))
        if image is not None:
            self.image = image

        self.font = pygame.font.Font("freesansbold.ttf", int(size[1]*7//9 - self.image.get_height()))
        if font is not None:
            self.font = font

        self.text = text
        self.text_surface = pygame.Surface((0, 0))
        if self.text is not None:
            self.text_surface = self.font.render(self.text, True, self.foreground[0])

        self.disabled = disabled

        self.command = command

        self.clicked = False

    def draw(self, screen: pygame.Surface):
        screen.blit(self.surface, self.surface_rect)

    def set_text(self, text: Optional[str] = None):
        self.text = text
        self.text_surface = pygame.Surface((0, 0))
        if self.text is not None:
            self.text_surface = self.font.render(self.text, True, self.foreground[0])

    def set_text_color(self, color: Union[str, pgClr]):
        if self.text is not None:
            self.text_surface = self.font.render(self.text, True, color)

    def draw_foreground(self):
        width = self.image.get_width()
        if self.text_surface.get_width() > width:
            width = self.text_surface.get_width()
        height = self.image.get_height()+self.text_surface.get_height()+6
        foreground_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        foreground_rect = foreground_surface.get_rect()
        foreground_rect.center = (self.surface.get_width()/2, self.surface.get_height()/2)

        image_rect = self.image.get_rect()
        image_rect.midtop = (width/2, 2)
        foreground_surface.blit(self.image, image_rect)

        text_rect = self.text_surface.get_rect()
        text_rect.midbottom = (width/2, height-2)
        foreground_surface.blit(self.text_surface, text_rect)

        self.surface.blit(foreground_surface, foreground_rect)

    def update(self, mouse_position: tuple[float, float]):
        global mouse_in_use

        if self.disabled:
            pygame.draw.rect(self.surface, self.background[3], self.rect, 0, self.border_radius)
            pygame.draw.rect(self.surface, self.border_color[3], self.rect, self.border_width, self.border_radius)
            self.set_text_color(self.foreground[3])
            self.draw_foreground()
            if self.surface_rect.collidepoint(mouse_position):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_NO)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        else:
            if self.surface_rect.collidepoint(mouse_position) and not mouse_in_use:
                if pygame.mouse.get_pressed()[0] and not self.clicked:
                    pygame.draw.rect(self.surface, self.background[2], self.rect, 0, self.border_radius)
                    pygame.draw.rect(self.surface, self.border_color[2], self.rect,
                                     self.border_width, self.border_radius)
                    self.set_text_color(self.foreground[2])
                    self.draw_foreground()

                    self.command()
                    self.clicked = True
                    mouse_in_use = True

                if not pygame.mouse.get_pressed()[0]:
                    pygame.draw.rect(self.surface, self.background[1], self.rect, 0, self.border_radius)
                    pygame.draw.rect(self.surface, self.border_color[1], self.rect,
                                     self.border_width, self.border_radius)
                    self.set_text_color(self.foreground[1])
                    self.draw_foreground()
            else:
                pygame.draw.rect(self.surface, self.background[0], self.rect, 0, self.border_radius)
                pygame.draw.rect(self.surface, self.border_color[0], self.rect, self.border_width, self.border_radius)
                self.set_text_color(self.foreground[0])
                self.draw_foreground()

                self.clicked = False


class ToggleableButton(Button):
    def __init__(
        self, size: Union[tuple[float, float], list[float, float]],
        position: Union[tuple[float, float], list[float, float]],
        image: Optional[pygame.Surface] = None,
        text: Optional[str] = None,
        font: Optional[pygame.font.Font] = None,

        background: Union[
            tuple[str, str, str, str, str], list[str, str, str, str, str],
            tuple[pgClr, pgClr, pgClr, pgClr, pgClr], list[pgClr, pgClr, pgClr, pgClr, pgClr]
        ] = ("#efefef", "#e5e5e5", "#0a0a0a", "#000000", "#f7f7f7"),

        foreground: Union[
            tuple[str, str, str, str], list[str, str, str, str],
            tuple[pgClr, pgClr, pgClr, pgClr], list[pgClr, pgClr, pgClr, pgClr]
        ] = ("#0a0a0a", "#000000", "#efefef", "#e5e5e5", "#383838"),

        border_color: Union[
            tuple[str, str, str, str], list[str, str, str, str],
            tuple[pgClr, pgClr, pgClr, pgClr], list[pgClr, pgClr, pgClr, pgClr]
        ] = ("#0a0a0a", "#000000", "#efefef", "#e5e5e5", "#383838"),

        border_width: int = 1,
        border_radius: int = 4,
        disabled: bool = False,
        command: Callable = do_nothing
    ):
        super().__init__(
            size, position,
            image, text, font,
            background, foreground,
            border_color, border_width, border_radius,
            disabled, command
        )
        self.is_active = False

        self.linked_with = []

    def update(self, mouse_position: tuple[float, float]):
        global mouse_in_use

        if self.disabled:
            self.is_active = False
            pygame.draw.rect(self.surface, self.background[4], self.rect, 0, self.border_radius)
            pygame.draw.rect(self.surface, self.border_color[4], self.rect, self.border_width,
                             self.border_radius)
            self.set_text_color(self.foreground[4])
            self.draw_foreground()

        else:
            if self.is_active:
                self.command()

            if self.surface_rect.collidepoint(mouse_position) and not mouse_in_use:
                if self.is_active:
                    pygame.draw.rect(self.surface, self.background[3], self.rect, 0, self.border_radius)
                    pygame.draw.rect(self.surface, self.border_color[3], self.rect, self.border_width,
                                     self.border_radius)
                    self.set_text_color(self.foreground[3])
                    self.draw_foreground()
                else:
                    pygame.draw.rect(self.surface, self.background[1], self.rect, 0, self.border_radius)
                    pygame.draw.rect(self.surface, self.border_color[1], self.rect, self.border_width,
                                     self.border_radius)
                    self.set_text_color(self.foreground[1])
                    self.draw_foreground()

                if pygame.mouse.get_pressed()[0] and not self.clicked:
                    is_active = False
                    if not self.is_active:
                        for btn in self.linked_with:
                            btn.is_active = False
                        is_active = True
                        mouse_in_use = True
                    self.is_active = is_active
                    self.clicked = True
            else:
                if self.is_active:
                    pygame.draw.rect(self.surface, self.background[2], self.rect, 0, self.border_radius)
                    pygame.draw.rect(self.surface, self.border_color[2], self.rect, self.border_width,
                                     self.border_radius)
                    self.set_text_color(self.foreground[2])
                    self.draw_foreground()
                else:
                    pygame.draw.rect(self.surface, self.background[0], self.rect, 0, self.border_radius)
                    pygame.draw.rect(self.surface, self.border_color[0], self.rect, self.border_width,
                                     self.border_radius)
                    self.set_text_color(self.foreground[0])
                    self.draw_foreground()

            if not pygame.mouse.get_pressed()[0]:
                self.clicked = False


class Slider:
    def __init__(
        self, position: Union[tuple[float, float], list[float, float]],
        label: str = "",
        font: Optional[pygame.font.Font] = None,
        min_value: int = 0,
        max_value: int = 100,
        length: int = 170,
        line_width: int = 6,
        color: Union[str, pgClr] = "#000000"
    ):
        self.position = position

        self.font = pygame.font.Font("freesansbold.ttf", 20)
        if font is not None:
            self.font = font
        self.label = label

        self.min_value = min_value
        self.max_value = max_value
        self.value = min_value

        self.blob_x = self.position[0]-4

        self.color = color

        self.clicked = False

        self.length = length
        self.line_width = line_width

    def set_value(self, value):
        self.value = value
        self.blob_x = self.position[0]-4+self.length*(value-self.min_value)/(self.max_value-self.min_value)

    def draw(self, screen):
        label = self.font.render(self.label + ": " + str(self.value), True, self.color)
        screen.blit(label, (self.position[0], self.position[1]-self.font.get_height()-12))

        surface = pygame.Surface((self.length, self.line_width))
        pygame.draw.line(surface, self.color, (0, 0), (self.length, 0), self.line_width)
        surface.set_alpha(150)
        screen.blit(surface, self.position)

        pygame.draw.rect(screen, self.color, pygame.Rect(self.blob_x, self.position[1]-5, 8, 16))
        pygame.draw.circle(screen, self.color, (self.blob_x+4, self.position[1]-5), 4)
        pygame.draw.circle(screen, self.color, (self.blob_x+4, self.position[1]+11), 4)

    def update(self, mouse_position):
        global mouse_in_use

        cdtn = pygame.Rect(self.position[0], self.position[1]-9, self.length, 15).collidepoint(mouse_position)
        if cdtn and not mouse_in_use:
            if pygame.mouse.get_pressed()[0]:
                self.clicked = True
                mouse_in_use = True
        if not pygame.mouse.get_pressed()[0]:
            self.clicked = False
        if self.clicked:
            self.blob_x = pygame.mouse.get_pos()[0]-4
            if self.blob_x < self.position[0]-4:
                self.blob_x = self.position[0]-4
            if self.blob_x > self.position[0]+self.length-4:
                self.blob_x = self.position[0]+self.length-4
        self.value = int(self.min_value+(self.max_value-self.min_value)*(self.blob_x-self.position[0]+4)/self.length)


class ScrollBar:
    def __init__(
        self, position: Union[tuple[float, float], list[float, float]],
        width: int,
        height: int,
        linked_to: pygame.Surface,
        clipping_height: int,
        background: Union[str, pgClr] = "#f1f1f1",
        slider_color: Union[
            tuple[str, str, str], list[str, str, str],
            tuple[pgClr, pgClr, pgClr], list[pgClr, pgClr, pgClr]
        ] = ("#c1c1c1", "#a8a8a8", "#787878")
    ):
        self.surface = pygame.Surface((width, height))
        self.surface_rect = self.surface.get_rect()
        self.surface_rect.topleft = position

        self.linked_to = linked_to
        self.clipping_height = clipping_height

        self.slider = pygame.Rect(1, 0, width-2, height*clipping_height/linked_to.get_height())

        self.clicked = False
        self.rel = [0, 0]

        self.background = background
        self.slider_color = slider_color

    def draw(self, screen):
        screen.blit(self.surface, self.surface_rect)

    def update(self, mouse_position):
        global mouse_in_use

        self.surface.fill(self.background)
        if self.slider.collidepoint(mouse_position[0]-self.surface_rect.left, mouse_position[1]-self.surface_rect.top) and not mouse_in_use:
            pygame.draw.rect(self.surface, self.slider_color[1], self.slider)
            if pygame.mouse.get_pressed()[0] and not self.clicked:
                self.clicked = True
                mouse_in_use = True
                self.rel = self.slider.top-mouse_position[1]
        else:
            pygame.draw.rect(self.surface, self.slider_color[0], self.slider)

        if not pygame.mouse.get_pressed()[0]:
            self.clicked = False

        if self.clicked:
            pygame.draw.rect(self.surface, self.slider_color[2], self.slider)
            self.slider.top = mouse_position[1]+self.rel
            if self.slider.top < 0:
                self.slider.top = 0
            if self.slider.bottom > self.surface.get_height():
                self.slider.bottom = self.surface.get_height()

    def get_clip(self):
        return pygame.Rect(0, self.slider.top*self.linked_to.get_height()/self.surface_rect.height,
                           self.linked_to.get_width(), self.clipping_height)


class FilesScreen:
    def __init__(self, size: Union[tuple[int, int], list[int, int]],
                 position: Union[tuple[int, int], list[int, int]],
                 folder: str,
                 open_or_save: str):
        self.quit = False
        if open_or_save not in ["open", "save"]:
            self.quit = True
        # ______________________________________________________________________________________________________________

        self.size = size
        self.position = position
        self.screen = pygame.Surface(self.size)
        self.screen_rect = self.screen.get_rect()
        self.screen_rect.topleft = self.position
        # ______________________________________________________________________________________________________________

        self.title_bar_height = 30
        self.title_bar = pygame.Surface((self.size[0], self.title_bar_height))
        self.title_bar.fill("#efefef")
        self.titleBar_Rect = self.title_bar.get_rect()
        self.titleBar_Rect.topleft = (0, 0)

        self.quit_button = Button(
            (40, 30), (self.size[0]-20, 15),
            text="X", font=pygame.font.SysFont("arial", 20, bold=True),
            background=["#efefef", "#ff4444", "#444444"], foreground=["#000000", "#efefef", "#ffffff"],
            border_width=1, border_radius=0, command=self.exit
        )

        self.title = pygame.font.SysFont("calibri", 25, bold=True).render(open_or_save.upper(), False, "#000000")
        self.title_rect = self.title.get_rect()
        self.title_rect.midleft = (10, self.title_bar_height / 2)

        self.title_bar_clicked = False
        self.rel = 0
        # ______________________________________________________________________________________________________________

        self.bottomArea_height = 90
        self.bottom_area = pygame.Surface((self.size[0], self.bottomArea_height))
        self.bottom_area.fill("#f0f0f0")

        self.label_fileName = Label((10, 30), text="File Name: ", font=pygame.font.SysFont("calibri", 23))
        self.text_input = TextInput((50+self.size[0]/2, 30), length=380)

        self.ok_button = Button((80, 20), (360, 65), text="OK", command=lambda: self.exit(True))
        self.cancel_button = Button((80, 20), (460, 65), text="CANCEL", command=self.exit)

        self.text_input.draw(self.bottom_area)
        self.text_input.invalid_chars = ["\\", "/", "|", ":", "*", "<", ">", "?", "\""]

        # ______________________________________________________________________________________________________________

        self.files = os.listdir(folder)

        self.filesSurface_height = self.size[1]-self.title_bar_height-self.bottomArea_height
        height = self.filesSurface_height
        if height < 200 + ((len(self.files)-1)//3)*180:
            height = 200 + ((len(self.files)-1)//3)*180
        self.files_surface = pygame.Surface((self.size[0]-20, height))
        self.files_surface_clip = pygame.Rect(0, 0, self.size[0]-20, self.filesSurface_height)
        self.files_surface.fill("#ffffff")

        self.button_images = []

        for i in range(len(self.files)):
            extension = os.path.splitext(self.files[i])[1]
            if extension in [".png", ".jpg", ".jpeg"]:
                self.button_images.append(
                    pygame.transform.scale(pygame.image.load("MyPaintings/"+self.files[i]), (120, 120))
                )
            else:
                self.button_images.append(
                    pygame.Surface((120, 120))
                )
        self.file_buttons = [ToggleableButton(
            (140, 160), (90 + (i % 3)*160, 100 + (i//3)*180),
            image=self.button_images[i],
            text=self.files[i][:-4],
            font=pygame.font.Font("freesansbold.ttf", 17),
            background=["#ffffff", "#e5f3ff", "#cce8ff", "#cce8ff"],
            foreground=["#000000", "#000000", "#000000", "#000000"],
            border_color=["#ffffff", "#e5f3ff", "#99d1ff", "#99d1ff"],
            border_width=2,
            border_radius=0,
        ) for i in range(len(self.files))]
        for i in range(len(self.file_buttons)):
            self.file_buttons[i].linked_with = self.file_buttons[:i] + self.file_buttons[i + 1:]

        self.return_value = open_or_save + "|"
        # ______________________________________________________________________________________________________________

        self.scroll_bar = ScrollBar((500, self.title_bar_height), 20, self.filesSurface_height,
                                    self.files_surface, self.filesSurface_height)

    def draw_titleBar(self):
        self.screen.blit(self.title_bar, self.titleBar_Rect)
        self.title_bar.blit(self.title, self.title_rect)
        pygame.draw.rect(self.title_bar, "#000000", self.titleBar_Rect, 1)

    def draw_files_surface(self):
        self.screen.blit(self.files_surface.subsurface(self.files_surface_clip), (0, self.title_bar_height))

    def draw_bottom_area(self):
        self.screen.blit(self.bottom_area, (0, self.size[1]-self.bottomArea_height))

    def draw(self, screen):
        screen.blit(self.screen, self.screen_rect)
        pygame.draw.rect(screen, "#000000", pygame.Rect(self.position, self.size), 1)
        self.text_input.draw(self.bottom_area)

    def update_title_bar(self, mouse_position):
        self.draw_titleBar()
        mouse_pos = (mouse_position[0] - self.position[0], mouse_position[1] - self.position[1])

        self.quit_button.draw(self.title_bar)
        self.quit_button.update(mouse_pos)

        if self.titleBar_Rect.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0] and not self.title_bar_clicked:
                self.rel = mouse_pos
                self.title_bar_clicked = True

        if not pygame.mouse.get_pressed()[0]:
            self.title_bar_clicked = False

        if self.title_bar_clicked:
            self.position = (mouse_position[0] - self.rel[0], mouse_position[1] - self.rel[1])
            self.screen_rect.topleft = self.position

    def update_files_surface(self, mouse_position):
        self.draw_files_surface()
        mouse_pos = (
            mouse_position[0] - self.position[0],
            mouse_position[1] - self.position[1] - self.title_bar_height + self.files_surface_clip.top
        )

        for i in range(len(self.file_buttons)):
            self.file_buttons[i].draw(self.files_surface)
            self.file_buttons[i].update(mouse_pos)
            if self.file_buttons[i].is_active:
                self.set_text(self.files[i])

        self.scroll_bar.draw(self.screen)
        self.scroll_bar.update((mouse_pos[0], mouse_pos[1]+self.title_bar_height))
        self.files_surface_clip = self.scroll_bar.get_clip()

    def update_bottom_area(self, mouse_position, event):
        self.draw_bottom_area()
        mouse_pos = (mouse_position[0] - self.position[0],
                     mouse_position[1] - self.position[1] - self.size[1] + self.bottomArea_height)

        self.label_fileName.draw(self.bottom_area)

        self.ok_button.draw(self.bottom_area)
        self.ok_button.update(mouse_pos)

        self.cancel_button.draw(self.bottom_area)
        self.cancel_button.update(mouse_pos)

        self.text_input.draw(self.bottom_area)
        self.text_input.update(mouse_pos, event)

    def update(self, mouse_position, event):
        self.update_title_bar(mouse_position)
        self.update_files_surface(mouse_position)
        self.update_bottom_area(mouse_position, event)

    def set_text(self, text):
        self.text_input.text = text

    def exit(self, ok_clicked=False):
        if ok_clicked:
            self.return_value += self.text_input.text
        self.quit = True
