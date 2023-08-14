import pygame
import pygame.freetype
from client.app import App


class Widget:
    def __init__(self, x, y, width, height, anchor='center'):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.anchor = anchor
        self.rect: pygame.Rect

        self.disabled = False
        self.hovered = False


class Button(Widget):
    def __init__(self, x, y, width, height, label, anchor, align='left', border_width=1):
        super().__init__(x, y, width, height, anchor)
        self.label = label
        self.align = align
        self.border_width = border_width
        self.padding = 10
        self.text_colour = (0, 0, 0)

        font_size = int(0.75 * (height - 2 * self.padding))
        self.font = pygame.freetype.Font('./Assets/UnivaNova-Regular.ttf', font_size)
        self.rect = pygame.Rect(0, 0, width, height)
        setattr(self.rect, anchor, (x, y))  # Position rect

    def draw_text(self):
        text_surf, text_rect = self.font.render(self.label, self.text_colour)
        if self.align == 'left':
            text_rect.midleft = self.rect.left + self.padding, self.rect.centery
        if self.align == 'center':
            text_rect.center = self.rect.center
        if self.align == 'right':
            text_rect.midright = self.rect.right - self.padding, self.rect.centery

        App.window.blit(text_surf, text_rect)

    def update(self):
        if not self.disabled:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            if self.rect.collidepoint((mouse_x, mouse_y)):
                self.hovered = True
                self.text_colour = (255, 255, 255)
            else:
                self.hovered = False
                self.text_colour = (0, 0, 0)

    def draw(self):
        if not self.disabled:
            if self.hovered:
                pygame.draw.rect(App.window, (0, 0, 0), self.rect)
        else:
            pygame.draw.rect(App.window, (128, 128, 128), self.rect)

        self.draw_text()

        if self.border_width != 0:
            pygame.draw.rect(App.window, (0, 0, 0), self.rect, width=self.border_width)