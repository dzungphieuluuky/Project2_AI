import pygame
from typing import Union
from config import *

pygame.init()
class Button:
    # initialize button class with callback function
    def __init__(self, present : Union[str, pygame.Surface], x: float, y: float, width: float, height: float, color: tuple[int, int, int], callback: callable, expandable = True) -> None:
        self.rect = pygame.Rect(x, y, width, height)
        self.present = present
        self.color = color
        # callback function to call the function of the button
        self.callback = callback
        self.expandable = expandable
        self.last_hovered = False
        self.is_hovered = False
        self.icons = []

    def draw_button(self, surface: pygame.surface) -> None:
        if self.icons:
            padding = 10
            spacing = 5
            current_x = self.rect.x + padding
            for icon_surf in self.icons:
                icon_rect = icon_surf.get_rect(centery=self.rect.centery, left=current_x)
                if icon_rect.right > self.rect.right - padding:
                    break
                surface.blit(icon_surf, icon_rect)
                current_x += icon_surf.get_width() + spacing
        else:
            present_surf = self.present
            if isinstance(self.present, str):
                present_surf = button_font.render(self.present, True, WHITE)
            if self.is_hovered and self.expandable:
                present_surf = pygame.transform.scale_by(present_surf, 1.1)
                if isinstance(self.present, str):
                    pygame.draw.rect(surface, self.color, self.rect.scale_by(1.1, 1.1), border_radius=15)
                    if self.last_hovered == False:
                        hover_sound.play()
            else:
                if isinstance(self.present, str):
                    pygame.draw.rect(surface, self.color, self.rect, border_radius=15)
            present_rect = present_surf.get_rect(center=self.rect.center)
            surface.blit(present_surf, present_rect)
        self.last_hovered = self.is_hovered

    def handle_event(self, event: pygame.event) -> None:
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif self.is_hovered and (event.type == pygame.MOUSEBUTTONDOWN or
                                  event.type == pygame.KEYDOWN and event.key in [pygame.K_RETURN, pygame.K_SPACE]):
            if self.expandable:
                click_sound.play()
                self.callback()
    
    def set_text(self, text: str) -> None:
        self.icons = []
        if isinstance(self.present, str):
            self.present = text
    
    def set_surface(self, surf: pygame.Surface) -> None:
        self.icons = []
        if isinstance(self, pygame.Surface):
            self.present = surf
    
    def set_icons(self, icons) -> None:
        self.icons = icons


class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = WHITE
        self.text = text
        self.active = False
        self.just_got_clicked = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            if self.active:
                self.just_got_clicked = True
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if self.just_got_clicked:
                    self.text = ""
                    self.just_got_clicked = False
                self.text += event.unicode

    def draw_box(self, surface):
        color = LIGHT_GRAY if self.active else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=5)
        text_surface = FONT_MEDIUM.render(self.text, True, BLACK)
        surface.blit(text_surface, (self.rect.x + 8, self.rect.y + 8))