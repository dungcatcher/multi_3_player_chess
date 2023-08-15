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

        self.text_colour = (0, 0, 0)
        self.padding = 10
        font_size = int(0.75 * (height - 2 * self.padding))
        self.font = pygame.freetype.Font('../Assets/UnivaNova-Regular.ttf', font_size)

        self.disabled = False
        self.hovered = False


class Button(Widget):
    def __init__(self, x, y, width, height, label, anchor, align='left', border_width=1):
        super().__init__(x, y, width, height, anchor)
        self.label = label
        self.align = align
        self.border_width = border_width

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


class TextBox(Widget):
    def __init__(self, x, y, width, height, anchor, align='left', border_width=1, hide_text=False):
        super().__init__(x, y, width, height, anchor)
        self.align = align
        self.border_width = border_width
        self.hide_text = hide_text

        self.rect = pygame.Rect(0, 0, width, height)
        setattr(self.rect, anchor, (x, y))  # Position rect

        self.text = ''
        self.text_rect: pygame.Rect
        self.selected = False
        self.show_cursor = True
        self.next_step_time = 0

    def draw_text(self):
        if not self.hide_text:
            text_surf, text_rect = self.font.render(self.text, self.text_colour)
        else:
            text_surf, text_rect = self.font.render(len(self.text) * 'x', self.text_colour)

        if self.align == 'left':
            text_rect.midleft = self.rect.left + self.padding, self.rect.centery
        if self.align == 'center':
            text_rect.center = self.rect.center
        if self.align == 'right':
            text_rect.midright = self.rect.right - self.padding, self.rect.centery

        self.text_rect = text_rect

        App.window.blit(text_surf, text_rect)

    def handle_event(self, event):
        if self.selected:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.key == pygame.K_RETURN:
                    pass
                else:
                    self.text += event.unicode

    def update(self):
        if not self.disabled:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            if self.rect.collidepoint((mouse_x, mouse_y)):
                self.hovered = True
            else:
                self.hovered = False

            current_time = pygame.time.get_ticks()
            if current_time > self.next_step_time:
                self.next_step_time += 530
                self.show_cursor = True if not self.show_cursor else False

    def draw(self):
        if not self.disabled:
            if self.border_width != 0:
                pygame.draw.rect(App.window, (0, 0, 0), self.rect, width=self.border_width)

            self.draw_text()

            if self.selected:
                if self.show_cursor:
                    cursor_rect = pygame.Rect(self.text_rect.right, self.text_rect.top, 2, self.text_rect.height)
                    pygame.draw.rect(App.window, (0, 0, 0), cursor_rect)
