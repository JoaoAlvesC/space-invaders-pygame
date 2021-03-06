from itertools import count
from time import time
from venv import create
from pygame import mixer
import pygame
from pygame.locals import *
import random

pygame.init()
mixer.init()

mixer.music.load("sound/background.mp3")
mixer.music.play(-1)
mixer.music.set_volume(0.05)

red = (255, 0, 0)
green = (0, 255, 0)
white = (255, 255, 255)

clock = pygame.time.Clock()
fps = 60

screen_width = 600
screen_height = 800
image = pygame.image.load("img/ifrs.png")

rows = 5
cols = 5

alien_cooldown = 1300
last_alien_shot = pygame.time.get_ticks()
countdown = 3
last_count = pygame.time.get_ticks()
game_over = 0
score = 0
resize_timer = 200
last_resize = pygame.time.get_ticks()
max_active_bullets = 6
difficulty = 1

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Invasive drugs')
bg = pygame.image.load("img/bg.png")

font30 = pygame.font.SysFont('Constantia', 30)
font40 = pygame.font.SysFont('Constantia', 40)

explosion_fx = pygame.mixer.Sound("sound/explosion.wav")
explosion_fx.set_volume(0.25)

explosion2_fx = pygame.mixer.Sound("sound/explosion2.wav")
explosion_fx.set_volume(0.25)

powerup_fx = pygame.mixer.Sound("sound/sucess.wav")
powerup_fx.set_volume(0.25)

laser_fx = pygame.mixer.Sound("sound/laser.wav")
laser_fx.set_volume(0.15)

def draw_bg():
    screen.blit(bg, (0,0))
    #screen.blit(image, (10, screen_height - 64))

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

class Spaceship(pygame.sprite.Sprite):
    def __init__(self, x, y, health):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/spaceship.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.health_start = health
        self.health_remaining = health
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        speed = 8
        cooldown = 500
        game_over = 0

        key = pygame.key.get_pressed()

        if key[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= speed
        
        if key[pygame.K_RIGHT] and self.rect.right < screen_width:
            self.rect.x += speed

        if key[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= speed

        if key[pygame.K_DOWN] and self.rect.bottom < screen_height:
            self.rect.y += speed

        time_now = pygame.time.get_ticks()

        if key[pygame.K_SPACE] and time_now - self.last_shot > cooldown:
            bullet = Bullets(self.rect.centerx, self.rect.top)
            bullet_group.add(bullet)
            laser_fx.play()
            self.last_shot = time_now

        self.mask = pygame.mask.from_surface(self.image)

        pygame.draw.rect(screen, red, (self.rect.x, (self.rect.bottom + 10), self.rect.width, 15))

        if self.health_remaining > 0:
            pygame.draw.rect(screen, green, (self.rect.x, (self.rect.bottom + 10), int(self.rect.width * (self.health_remaining / self.health_start)), 15))
            
        elif self.health_remaining <= 0:
            explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(explosion)
            self.kill()
            game_over = -1
        return game_over

class Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/bullet1.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]

    def update(self):
        self.rect.y -= 5
        if self.rect.bottom < 0:
            self.kill()
        if pygame.sprite.spritecollide(self, alien_group, True, pygame.sprite.collide_mask):
            self.kill()
            global score 
            score += 2
            explosion_fx.play()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosion)
        
class Aliens(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/alien" + str(random.randint(1, 3)) + ".png")
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.move_counter = 0
        self.move_direction = 1

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1

        self.mask = pygame.mask.from_surface(self.image)
        
        if abs(self.move_counter) > 75:
            self.move_direction *= -1
            self.move_counter *= self.move_direction
        
        if pygame.sprite.spritecollide(self, spaceship_group, True, pygame.sprite.collide_mask):
            spaceship.health_remaining = 0
            explosion2_fx.play()
            #self.kill()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion)
    
class AlienBullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/alien_bullet.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]

    def update(self):
        self.rect.y += 2
        if self.rect.top > screen_height:
            self.kill()

        if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
            spaceship.health_remaining -= 1
            explosion2_fx.play()
            self.kill()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion)

        if pygame.sprite.spritecollide(self, bullet_group, True):
            explosion2_fx.play()
            self.kill()
            global score
            score += 1
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion)

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        pygame.sprite.Sprite.__init__(self)
        self.images = []

        for num in range(1,6):
            img = pygame.image.load(f"img/exp{num}.png")

            if size == 1:
                img = pygame.transform.scale(img, (20, 20))
            if size == 2:
                img = pygame.transform.scale(img, (40, 40))
            if size == 3:
                img = pygame.transform.scale(img, (200, 200))

            self.images.append(img)

        self.index = 0    
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.counter = 0

    def update(self):
        explosion_speed = 3
        self.counter += 1
        
        if self.counter >= explosion_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]

        if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
            self.kill()

class ExtraLife(pygame.sprite.Sprite):
    
    def __init__(self, x, y, path):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(path)
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]   

    def update(self):
        key = pygame.key.get_pressed()

        if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
            self.kill()
            powerup_fx.play()
            spaceship.health_remaining += 1

spaceship_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group()
alienBullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
extraLife_group = pygame.sprite.Group()


def create_aliens():
    for row in range(rows):
        for item in range(cols):
            alien = Aliens(100 + item * 100, 100 + row * 70)
            alien_group.add(alien)

create_aliens()

spaceship = Spaceship(int(screen_width / 2), screen_width - 10, 3 )
spaceship_group.add(spaceship)


extraLife = ExtraLife(40, screen_height - 80, "img/ifrs.png" )
extraLife2 = ExtraLife(screen_width - 40, screen_height - 80, "img/computacao.png" )
extraLife_group.add(extraLife)
extraLife_group.add(extraLife2)

run = True
while run:

    clock.tick(fps)

    draw_bg()

    if countdown == 0:

        time_now = pygame.time.get_ticks()

        print(alien_cooldown)
        if score >= 10:
            alien_cooldown = 1100
            max_active_bullets = 8
            difficulty = 2
        if score >= 20:
            alien_cooldown = 900
            max_active_bullets = 10
            difficulty = 3
        if score >= 30:
            alien_cooldown = 500
            max_active_bullets = 13
            difficulty = 4
        if score >= 40:
            max_active_bullets = 20
            difficulty = 5
        if score >= 45:
            max_active_bullets = 35
            difficulty = 6
        

        if time_now - last_alien_shot > alien_cooldown and len(alienBullet_group) < max_active_bullets and len(alien_group) > 0:
            attacking_alien = random.choice(alien_group.sprites())
            alien_bullet = AlienBullets(attacking_alien.rect.centerx, attacking_alien.rect.bottom)
            alienBullet_group.add(alien_bullet)
            last_alien_shot = time_now

        if len(alien_group) == 0:
            game_over = 1


        if game_over == 0:    
            game_over = spaceship.update()
            bullet_group.update()
            alien_group.update()
            alienBullet_group.update()
            extraLife_group.update()
            
        else: 
            if game_over == -1:
                draw_text("GAME OVER!", font40, white, int(screen_width / 2 - 100), int(screen_height / 2 + 50))
            if game_over == 1:
                draw_text("YOU WIN!!", font40, white, int(screen_width / 2 - 110), int(screen_height / 2 + 50))
    
    if countdown > 0:
        draw_text("GET READY!", font40, white, int(screen_width / 2 - 110), int(screen_height / 2 + 50))
        draw_text(str(countdown), font30, white, int(screen_width / 2 - 10), int(screen_height / 2 + 100))
        count_timer = pygame.time.get_ticks()
        if count_timer - last_count > 1000:
            countdown -= 1
            last_count = count_timer

    explosion_group.update()

    spaceship_group.draw(screen)
    bullet_group.draw(screen)
    alien_group.draw(screen)
    alienBullet_group.draw(screen)
    explosion_group.draw(screen)
    extraLife_group.draw(screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    draw_text("SCORE: " + str(score), font30, white, 10, 10)
    draw_text("Dificuldade: " + str(difficulty), font30, white, screen_width - 175, 10)
    
    pygame.display.update()

pygame.quit()