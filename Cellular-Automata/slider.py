import pygame

class Slider:
    def __init__(self, rect: pygame.Rect, minVal, maxVal, initial):
        self.rect = rect
        self.minVal = minVal
        self.maxVal = maxVal
        self.t = (initial - minVal) / (maxVal - minVal)
        self.handle_radius = max(6, rect.height // 2)
        self.dragging = False

    @property
    def value(self):
        return self.minVal + self.t * (self.maxVal - self.minVal)
    
    def handle_pos(self):
        x = self.rect.x + int(self.t * self.rect.width)
        y = self.rect.centery
        return x, y
    
    def draw(self, surf):
        pygame.draw.rect(surf, (50,50,50), self.rect)
        hx, hy = self.handle_pos()
        pygame.draw.circle(surf, (200,200,200), (hx,hy), self.handle_radius)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self._point_in_circle(event.pos, self.handle_pos(), self.handle_radius) or self.rect.collidepoint(event.pos):
                self.dragging = True
                self._update_t_from_pos(event.pos)
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._update_t_from_pos(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

    def _point_in_circle(self, point, center, radius):
        dx = point[0] - center[0]
        dy = point[1] - center[1]
        return dx * dx +dy * dy <= radius * radius

    def _update_t_from_pos(self, pos):
        x = pos[0] - self.rect.x
        self.t = min(1, min(1.0, x / self.rect.width))
        