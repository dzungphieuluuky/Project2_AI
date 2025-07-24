import pygame
from typing import Union

from sound import *
from font import *

WHITE = (255, 255, 255)
BLUE = (0, 100, 255)
DARK_BLUE = (0, 80, 200)
BLACK = (0, 0, 0)

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

    def draw_button(self, surface: pygame.surface) -> None:
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

        self.last_hovered = self.is_hovered
        present_rect = present_surf.get_rect(center=self.rect.center)
        surface.blit(present_surf, present_rect)

    def handle_event(self, event: pygame.event) -> None:
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif self.is_hovered and (event.type == pygame.MOUSEBUTTONDOWN or
                                  event.type == pygame.KEYDOWN and event.key in [pygame.K_RETURN, pygame.K_SPACE]):
            if self.expandable:
                click_sound.play()
            self.callback()
    
    def set_text(self, text: str) -> None:
        if isinstance(self.present, str):
            self.present = text