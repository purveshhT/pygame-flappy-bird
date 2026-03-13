import pygame
import sys
import random
import math
import json
import os
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 288
SCREEN_HEIGHT = 512
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
LIGHT_BLUE = (135, 206, 235)

class GameState(Enum):
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3

class PowerUpType(Enum):
    SHIELD = 1
    SLOW_MOTION = 2
    MAGNET = 3

class PowerUp:
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.power_type = power_type
        self.radius = 15
        self.collected = False
        self.animation_time = 0
        
    def update(self, dt):
        self.animation_time += dt
        
    def draw(self, screen):
        if not self.collected:
            # Animate the power-up
            pulse = math.sin(self.animation_time * 5) * 0.2 + 1
            radius = int(self.radius * pulse)
            
            if self.power_type == PowerUpType.SHIELD:
                pygame.draw.circle(screen, BLUE, (int(self.x), int(self.y)), radius)
                pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), radius, 2)
            elif self.power_type == PowerUpType.SLOW_MOTION:
                pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), radius)
                pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), radius, 2)
            elif self.power_type == PowerUpType.MAGNET:
                pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), radius)
                pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), radius, 2)
    
    def check_collision(self, bird):
        if self.collected:
            return False
        
        distance = math.sqrt((self.x - bird.x) ** 2 + (self.y - bird.y) ** 2)
        return distance < (self.radius + bird.radius)

class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 15
        self.velocity_y = 0
        self.velocity_x = 0
        self.gravity = 0.5
        self.jump_strength = -8
        self.rotation = 0
        self.animation_frame = 0
        self.animation_time = 0
        self.shield_active = False
        self.shield_time = 0
        self.slow_motion_active = False
        self.slow_motion_time = 0
        self.magnet_active = False
        self.magnet_time = 0
        
        # Load bird sprites
        self.sprites = []
        try:
            for i in range(3):
                sprite = pygame.image.load(f'assets/bird_{i}.png')
                self.sprites.append(sprite)
        except:
            # Fallback to simple drawing if sprites not found
            self.sprites = None
        
    def update(self, dt):
        # Update power-ups
        if self.shield_active:
            self.shield_time -= dt
            if self.shield_time <= 0:
                self.shield_active = False
                
        if self.slow_motion_active:
            self.slow_motion_time -= dt
            if self.slow_motion_time <= 0:
                self.slow_motion_active = False
                
        if self.magnet_active:
            self.magnet_time -= dt
            if self.magnet_time <= 0:
                self.magnet_active = False
        
        # Apply gravity
        gravity_multiplier = 0.3 if self.slow_motion_active else 1.0
        self.velocity_y += self.gravity * gravity_multiplier
        
        # Update position
        self.y += self.velocity_y
        self.x += self.velocity_x
        
        # Apply air resistance to horizontal velocity
        self.velocity_x *= 0.98
        
        # Update rotation based on velocity
        self.rotation = min(90, max(-30, self.velocity_y * 3))
        
        # Update animation
        self.animation_time += dt
        if self.animation_time > 0.1:
            self.animation_frame = (self.animation_frame + 1) % 3
            self.animation_time = 0
    
    def flap(self, strength=1.0, game=None):
        self.velocity_y = self.jump_strength * strength
        if game and 'flap' in game.sounds:
            game.sounds['flap'].play()
        
    def slingshot(self, target_x, target_y):
        # Calculate direction and distance
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            # Normalize and apply force
            force = min(distance / 50, 2.0)  # Limit force
            self.velocity_x = (dx / distance) * force * 3
            self.velocity_y = (dy / distance) * force * 3 - 2  # Slight upward bias
    
    def draw(self, screen):
        # Draw shield effect
        if self.shield_active:
            shield_radius = self.radius + 5
            pygame.draw.circle(screen, BLUE, (int(self.x), int(self.y)), shield_radius, 3)
        
        # Draw bird sprite or fallback
        if self.sprites:
            # Use sprite animation
            sprite = self.sprites[self.animation_frame]
            # Rotate sprite based on velocity
            rotated_sprite = pygame.transform.rotate(sprite, -self.rotation)
            sprite_rect = rotated_sprite.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(rotated_sprite, sprite_rect)
        else:
            # Fallback drawing
            bird_color = LIGHT_BLUE
            pygame.draw.circle(screen, bird_color, (int(self.x), int(self.y)), self.radius)
            
            # Draw eye
            eye_x = int(self.x + 5)
            eye_y = int(self.y - 3)
            pygame.draw.circle(screen, WHITE, (eye_x, eye_y), 4)
            pygame.draw.circle(screen, BLACK, (eye_x, eye_y), 2)
            
            # Draw beak
            beak_points = [
                (int(self.x + self.radius), int(self.y)),
                (int(self.x + self.radius + 8), int(self.y - 2)),
                (int(self.x + self.radius + 8), int(self.y + 2))
            ]
            pygame.draw.polygon(screen, YELLOW, beak_points)

class Pipe:
    def __init__(self, x, gap_height):
        self.x = x
        self.gap_height = gap_height
        self.gap_y = random.randint(100, SCREEN_HEIGHT - 200)
        self.width = 50
        self.passed = False
        
    def update(self, speed):
        self.x -= speed
        
    def draw(self, screen):
        # Top pipe
        top_height = self.gap_y - self.gap_height // 2
        pygame.draw.rect(screen, GREEN, (self.x, 0, self.width, top_height))
        pygame.draw.rect(screen, WHITE, (self.x, 0, self.width, top_height), 2)
        
        # Bottom pipe
        bottom_y = self.gap_y + self.gap_height // 2
        bottom_height = SCREEN_HEIGHT - bottom_y
        pygame.draw.rect(screen, GREEN, (self.x, bottom_y, self.width, bottom_height))
        pygame.draw.rect(screen, WHITE, (self.x, bottom_y, self.width, bottom_height), 2)
    
    def check_collision(self, bird):
        if (bird.x + bird.radius > self.x and 
            bird.x - bird.radius < self.x + self.width):
            
            # Check if bird is in the gap
            if (bird.y - bird.radius < self.gap_y - self.gap_height // 2 or 
                bird.y + bird.radius > self.gap_y + self.gap_height // 2):
                return True
        return False

class CursorTrail:
    def __init__(self):
        self.particles = []
        
    def add_particle(self, x, y):
        self.particles.append({
            'x': x,
            'y': y,
            'life': 1.0,
            'size': 3
        })
        
    def update(self, dt):
        for particle in self.particles[:]:
            particle['life'] -= dt * 2
            particle['size'] *= 0.95
            if particle['life'] <= 0:
                self.particles.remove(particle)
                
    def draw(self, screen):
        for particle in self.particles:
            alpha = int(particle['life'] * 255)
            color = (*WHITE, alpha)
            pygame.draw.circle(screen, WHITE, 
                             (int(particle['x']), int(particle['y'])), 
                             int(particle['size']))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Flapp Bird")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Game state
        self.state = GameState.MENU
        self.score = 0
        self.best_score = self.load_best_score()
        
        # Game objects
        self.bird = Bird(50, SCREEN_HEIGHT // 2)
        self.pipes = []
        self.power_ups = []
        self.cursor_trail = CursorTrail()
        
        # Mouse controls
        self.mouse_pressed = False
        self.mouse_hold_time = 0
        self.mouse_start_pos = None
        self.dragging = False
        
        # Game settings
        self.pipe_speed = 2
        self.pipe_spawn_timer = 0
        self.pipe_spawn_interval = 2.0
        self.gap_height = 150
        self.power_up_spawn_timer = 0
        
        # Load cursor sprite
        try:
            self.cursor_sprite = pygame.image.load('assets/cursor.png')
        except:
            self.cursor_sprite = None
            
        # Load background
        try:
            self.background = pygame.image.load('assets/background.png')
        except:
            self.background = None
            
        # Load sounds
        self.sounds = {}
        try:
            self.sounds['flap'] = pygame.mixer.Sound('assets/flap.wav')
            self.sounds['score'] = pygame.mixer.Sound('assets/score.wav')
            self.sounds['game_over'] = pygame.mixer.Sound('assets/game_over.wav')
            self.sounds['power_up'] = pygame.mixer.Sound('assets/power_up.wav')
        except:
            # Sounds will be disabled if not found
            self.sounds = {}
        
        # Hide system cursor
        pygame.mouse.set_visible(False)
        
    def load_best_score(self):
        try:
            if os.path.exists('best_score.json'):
                with open('best_score.json', 'r') as f:
                    data = json.load(f)
                    return data.get('best_score', 0)
        except:
            pass
        return 0
    
    def save_best_score(self):
        try:
            with open('best_score.json', 'w') as f:
                json.dump({'best_score': self.best_score}, f)
        except:
            pass
    
    def reset_game(self):
        self.bird = Bird(50, SCREEN_HEIGHT // 2)
        self.pipes = []
        self.power_ups = []
        self.score = 0
        self.pipe_speed = 2
        self.gap_height = 150
        self.pipe_spawn_timer = 0
        self.power_up_spawn_timer = 0
        
    def spawn_pipe(self):
        self.pipes.append(Pipe(SCREEN_WIDTH, self.gap_height))
        
    def spawn_power_up(self):
        if random.random() < 0.1:  # 10% chance
            power_type = random.choice(list(PowerUpType))
            x = SCREEN_WIDTH + 50
            y = random.randint(100, SCREEN_HEIGHT - 100)
            self.power_ups.append(PowerUp(x, y, power_type))
    
    def handle_input(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()
        keys = pygame.key.get_pressed()
        
        # Add cursor trail
        self.cursor_trail.add_particle(mouse_pos[0], mouse_pos[1])
        
        if self.state == GameState.PLAYING:
            # Handle spacebar input
            if keys[pygame.K_SPACE]:
                if not hasattr(self, 'space_pressed') or not self.space_pressed:
                    self.space_pressed = True
                    self.bird.flap(1.0, self)  # Quick flap on spacebar
            else:
                self.space_pressed = False
            
            # Handle mouse input
            if mouse_buttons[0]:  # Left mouse button
                if not self.mouse_pressed:
                    self.mouse_pressed = True
                    self.mouse_start_pos = mouse_pos
                    self.mouse_hold_time = 0
                    
                    # Check if clicking on bird for power boost
                    distance_to_bird = math.sqrt((mouse_pos[0] - self.bird.x)**2 + 
                                               (mouse_pos[1] - self.bird.y)**2)
                    if distance_to_bird < self.bird.radius + 20:
                        self.bird.flap(1.5, self)  # Power boost
                else:
                    self.mouse_hold_time += dt
                    
                    # Check for drag
                    if self.mouse_start_pos:
                        drag_distance = math.sqrt((mouse_pos[0] - self.mouse_start_pos[0])**2 + 
                                                (mouse_pos[1] - self.mouse_start_pos[1])**2)
                        if drag_distance > 20:
                            self.dragging = True
            else:
                if self.mouse_pressed:
                    if self.dragging and self.mouse_start_pos:
                        # Slingshot
                        self.bird.slingshot(mouse_pos[0], mouse_pos[1])
                    elif self.mouse_hold_time > 0.1:
                        # Charged flap
                        strength = min(2.0, 1.0 + self.mouse_hold_time)
                        self.bird.flap(strength, self)
                    else:
                        # Quick flap
                        self.bird.flap(1.0, self)
                    
                    self.mouse_pressed = False
                    self.dragging = False
                    self.mouse_hold_time = 0
                    self.mouse_start_pos = None
    
    def update(self, dt):
        if self.state == GameState.PLAYING:
            # Update bird
            self.bird.update(dt)
            
            # Update pipes
            for pipe in self.pipes[:]:
                pipe.update(self.pipe_speed)
                
                # Check collision
                if pipe.check_collision(self.bird) and not self.bird.shield_active:
                    self.state = GameState.GAME_OVER
                    if self.score > self.best_score:
                        self.best_score = self.score
                        self.save_best_score()
                    if 'game_over' in self.sounds:
                        self.sounds['game_over'].play()
                
                # Check scoring
                if not pipe.passed and pipe.x + pipe.width < self.bird.x:
                    pipe.passed = True
                    self.score += 1
                    if 'score' in self.sounds:
                        self.sounds['score'].play()
                    
                    # Increase difficulty
                    if self.score % 10 == 0:
                        self.pipe_speed += 0.5
                        self.gap_height = max(100, self.gap_height - 10)
                
                # Remove off-screen pipes
                if pipe.x + pipe.width < 0:
                    self.pipes.remove(pipe)
            
            # Update power-ups
            for power_up in self.power_ups[:]: 
                power_up.update(dt)
                
                if power_up.check_collision(self.bird):
                    power_up.collected = True
                    if power_up.power_type == PowerUpType.SHIELD:
                        self.bird.shield_active = True
                        self.bird.shield_time = 5.0
                    elif power_up.power_type == PowerUpType.SLOW_MOTION:
                        self.bird.slow_motion_active = True
                        self.bird.slow_motion_time = 3.0
                    elif power_up.power_type == PowerUpType.MAGNET:
                        self.bird.magnet_active = True
                        self.bird.magnet_time = 4.0
                    
                    if 'power_up' in self.sounds:
                        self.sounds['power_up'].play()
                    self.power_ups.remove(power_up)
                elif power_up.x < -50:
                    self.power_ups.remove(power_up)
            
            # Spawn pipes
            self.pipe_spawn_timer += dt
            if self.pipe_spawn_timer >= self.pipe_spawn_interval:
                self.spawn_pipe()
                self.pipe_spawn_timer = 0
                
            # Spawn power-ups
            self.power_up_spawn_timer += dt
            if self.power_up_spawn_timer >= 10.0:  # Every 10 seconds
                self.spawn_power_up()
                self.power_up_spawn_timer = 0
            
            # Check bird boundaries
            if self.bird.y > SCREEN_HEIGHT or self.bird.y < 0:
                if not self.bird.shield_active:
                    self.state = GameState.GAME_OVER
                    if self.score > self.best_score:
                        self.best_score = self.score
                        self.save_best_score()
        
        # Update cursor trail
        self.cursor_trail.update(dt)
    
    def draw_cursor(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw custom cursor
        if self.cursor_sprite:
            cursor_rect = self.cursor_sprite.get_rect(center=mouse_pos)
            screen.blit(self.cursor_sprite, cursor_rect)
        else:
            # Fallback cursor
            pygame.draw.circle(screen, WHITE, mouse_pos, 8)
            pygame.draw.circle(screen, BLACK, mouse_pos, 8, 2)
        
        # Draw charge bar when holding
        if self.mouse_pressed and self.state == GameState.PLAYING:
            charge_width = min(100, self.mouse_hold_time * 50)
            bar_x = mouse_pos[0] - 50
            bar_y = mouse_pos[1] - 30
            
            # Background
            pygame.draw.rect(screen, GRAY, (bar_x, bar_y, 100, 10))
            # Charge
            pygame.draw.rect(screen, YELLOW, (bar_x, bar_y, charge_width, 10))
            pygame.draw.rect(screen, WHITE, (bar_x, bar_y, 100, 10), 2)
        
        # Draw slingshot line when dragging
        if self.dragging and self.mouse_start_pos and self.state == GameState.PLAYING:
            pygame.draw.line(screen, WHITE, self.mouse_start_pos, mouse_pos, 3)
    
    def draw(self):
        # Draw background
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(LIGHT_BLUE)
        
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.PLAYING:
            self.draw_game()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()
        
        # Draw cursor trail
        self.cursor_trail.draw(self.screen)
        
        # Draw custom cursor
        self.draw_cursor(self.screen)
        
        pygame.display.flip()
    
    def draw_menu(self):
        # Title
        title_text = self.font.render("Flapp Bird", True, BLACK)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 100))
        self.screen.blit(title_text, title_rect)
        
        # Instructions
        instructions = [
            "Spacebar: Quick flap",
            "Click: Quick flap",
            "Hold: Charge flap",
            "Drag: Slingshot",
            "Click bird: Power boost"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, BLACK)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, 150 + i * 25))
            self.screen.blit(text, text_rect)
        
        # Best score
        best_text = self.small_font.render(f"Best Score: {self.best_score}", True, BLACK)
        best_rect = best_text.get_rect(center=(SCREEN_WIDTH//2, 280))
        self.screen.blit(best_text, best_rect)
        
        # Play button
        play_text = self.font.render("Click to Play", True, BLACK)
        play_rect = play_text.get_rect(center=(SCREEN_WIDTH//2, 350))
        self.screen.blit(play_text, play_rect)
        
        # Check for play button click
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0] and play_rect.collidepoint(mouse_pos):
            self.state = GameState.PLAYING
            self.reset_game()
    
    def draw_game(self):
        # Draw pipes
        for pipe in self.pipes:
            pipe.draw(self.screen)
        
        # Draw power-ups
        for power_up in self.power_ups:
            power_up.draw(self.screen)
        
        # Draw bird
        self.bird.draw(self.screen)
        
        # Draw HUD
        score_text = self.font.render(str(self.score), True, BLACK)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, 50))
        self.screen.blit(score_text, score_rect)
        
        # Best score
        best_text = self.small_font.render(f"Best: {self.best_score}", True, BLACK)
        self.screen.blit(best_text, (10, 10))
        
        # Power-up indicators
        y_offset = 40
        if self.bird.shield_active:
            shield_text = self.small_font.render("Shield", True, BLUE)
            self.screen.blit(shield_text, (10, y_offset))
            y_offset += 20
            
        if self.bird.slow_motion_active:
            slow_text = self.small_font.render("Slow Motion", True, YELLOW)
            self.screen.blit(slow_text, (10, y_offset))
            y_offset += 20
            
        if self.bird.magnet_active:
            magnet_text = self.small_font.render("Magnet", True, RED)
            self.screen.blit(magnet_text, (10, y_offset))
    
    def draw_game_over(self):
        # Game over text
        game_over_text = self.font.render("Game Over", True, BLACK)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, 150))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Final score
        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, 200))
        self.screen.blit(score_text, score_rect)
        
        # Best score
        best_text = self.font.render(f"Best: {self.best_score}", True, BLACK)
        best_rect = best_text.get_rect(center=(SCREEN_WIDTH//2, 240))
        self.screen.blit(best_text, best_rect)
        
        # Restart button
        restart_text = self.font.render("Click to Restart", True, BLACK)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, 300))
        self.screen.blit(restart_text, restart_rect)
        
        # Check for restart button click
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0] and restart_rect.collidepoint(mouse_pos):
            self.state = GameState.PLAYING
            self.reset_game()
    
    def run(self):
        running = True
        
        while running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            self.handle_input(dt)
            self.update(dt)
            self.draw()
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
