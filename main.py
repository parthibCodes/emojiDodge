import pygame
import sys
import random
import time
import os

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Emoji Dodge Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 128, 0)
BLUE = (100, 149, 237)  # Day background
DARK_BLUE = (25, 25, 112)  # Night background
DARK_RED = (139, 0, 0)
GOLD = (255, 215, 0)
PURPLE = (128, 0, 128)

# Create sounds directory
sounds_dir = os.path.join(os.path.dirname(__file__), "sounds")
os.makedirs(sounds_dir, exist_ok=True)

# Sound management
def create_sound(name):
    path = os.path.join(sounds_dir, f"{name}.wav")
    if not os.path.exists(path):
        with open(path, 'wb') as f:
            f.write(b'')
    try:
        return pygame.mixer.Sound(path)
    except:
        class DummySound:
            def play(self): pass
        return DummySound()

# Load sounds
hit_sound = create_sound("hit")
game_over_sound = create_sound("game_over")
life_up_sound = create_sound("life_up")
combo_sound = create_sound("combo")
powerup_sound = create_sound("powerup")
fake_sound = create_sound("fake")

# Game settings
class GameSettings:
    def __init__(self):
        # Player settings
        self.player_size = 50
        self.player_speed = 8
        self.player_emojis = ['😎', '🐱', '🦸‍♂️']
        self.current_emoji_index = 0

        # Lives system
        self.max_lives = 3
        self.lives = self.max_lives
        self.invincibility_time = 1.5
        self.is_invincible = False
        self.last_hit_time = 0

        # Combo system
        self.combo_count = 0
        self.combo_threshold = 10
        self.combo_bonus = 50
        self.show_combo = False
        self.combo_display_time = 0
        self.combo_duration = 3

        # Day/Night cycle
        self.is_night_mode = False
        self.day_night_interval = 30
        self.last_day_night_switch = time.time()

        # Obstacle settings
        self.obstacle_size = 40
        self.base_obstacle_speed = 5
        self.obstacle_speed = self.base_obstacle_speed
        self.obstacle_spawn_rate = 30

        # Powerup settings
        self.powerup_size = 40
        self.powerup_speed = 3
        self.savior_spawn_interval = 15
        self.last_savior_spawn = time.time()

        # Slow time powerup
        self.slow_time_active = False
        self.slow_time_start = 0
        self.slow_time_duration = 5
        self.slow_time_interval = 20
        self.last_slow_time_spawn = time.time()

        # Game state
        self.score = 0
        self.survival_score = 0
        self.game_over = False
        self.game_over_overlay_alpha = 0

        # Timer for increasing difficulty
        self.start_time = time.time()
        self.last_difficulty_increase = self.start_time
        self.difficulty_increase_interval = 10

        # Spin wheel system
        self.spin_wheel_active = False
        self.spin_wheel_spinning = False
        self.spin_wheel_result = None


# Initialize game settings
settings = GameSettings()

# Player position
player_x = SCREEN_WIDTH // 2 - settings.player_size // 2
player_y = SCREEN_HEIGHT - settings.player_size - 10

# Game objects
obstacles = []
saviors = []
fake_saviors = []
slow_time_powerups = []

# Font for emoji
emoji_font = pygame.font.SysFont('segoe ui emoji', settings.player_size)
small_emoji_font = pygame.font.SysFont('segoe ui emoji', settings.obstacle_size)
text_font = pygame.font.SysFont(None, 28)

# Emoji renders
def update_emoji_renders():
    global player_emoji, heart_emoji, savior_emoji, fake_savior_emoji, slow_time_emoji, obstacle_emojis

    player_emoji = emoji_font.render(settings.player_emojis[settings.current_emoji_index], True, BLACK)
    heart_emoji = small_emoji_font.render('❤️', True, BLACK)
    savior_emoji = small_emoji_font.render('🛡️', True, BLACK)
    fake_savior_emoji = small_emoji_font.render('💔', True, BLACK)
    slow_time_emoji = small_emoji_font.render('⏳', True, BLACK)

    obstacle_emojis = [
        small_emoji_font.render('🔥', True, BLACK),
        small_emoji_font.render('💣', True, BLACK),
        small_emoji_font.render('🪨', True, BLACK),
        small_emoji_font.render('⚡', True, BLACK),
        small_emoji_font.render('🌪️', True, BLACK)
    ]

# Initialize emoji renders
update_emoji_renders()

# Game functions
def draw_player():
    if settings.is_invincible and int(time.time() * 10) % 2 == 0:
        return  # Flash effect when invincible
    screen.blit(player_emoji, (player_x, player_y))

def spawn_obstacle():
    x = random.randint(0, SCREEN_WIDTH - settings.obstacle_size)
    y = -settings.obstacle_size
    emoji = random.choice(obstacle_emojis)
    obstacles.append([x, y, emoji])

def spawn_savior():
    x = random.randint(0, SCREEN_WIDTH - settings.powerup_size)
    y = -settings.powerup_size

    # 1 in 4 chance to spawn a fake savior
    if random.randint(1, 4) == 1:
        fake_saviors.append([x, y])
    else:
        saviors.append([x, y])

def spawn_slow_time():
    x = random.randint(0, SCREEN_WIDTH - settings.powerup_size)
    y = -settings.powerup_size
    slow_time_powerups.append([x, y])

def draw_objects():
    # Draw obstacles
    for obstacle in obstacles:
        screen.blit(obstacle[2], (obstacle[0], obstacle[1]))

    # Draw real saviors
    for savior in saviors:
        glow_rect = pygame.Rect(savior[0]-5, savior[1]-5, settings.powerup_size+10, settings.powerup_size+10)
        pygame.draw.ellipse(screen, GOLD, glow_rect)
        screen.blit(savior_emoji, (savior[0], savior[1]))

    # Draw fake saviors
    for fake in fake_saviors:
        glow_rect = pygame.Rect(fake[0]-5, fake[1]-5, settings.powerup_size+10, settings.powerup_size+10)
        pygame.draw.ellipse(screen, RED, glow_rect)
        screen.blit(fake_savior_emoji, (fake[0], fake[1]))

    # Draw slow time powerups
    for powerup in slow_time_powerups:
        glow_rect = pygame.Rect(powerup[0]-5, powerup[1]-5, settings.powerup_size+10, settings.powerup_size+10)
        pygame.draw.ellipse(screen, PURPLE, glow_rect)
        screen.blit(slow_time_emoji, (powerup[0], powerup[1]))

def draw_lives():
    for i in range(settings.lives):
        screen.blit(heart_emoji, (SCREEN_WIDTH - 50 - i * 35, 15))

def draw_combo():
    if settings.show_combo:
        combo_text = emoji_font.render(f"+{settings.combo_bonus} COMBO! ⚡", True, GOLD)
        text_rect = combo_text.get_rect(center=(SCREEN_WIDTH//2, 100))
        screen.blit(combo_text, text_rect)

def update_obstacles():
    current_speed = settings.obstacle_speed
    if settings.slow_time_active:
        current_speed *= 0.5  # 50% slower when slow time is active

    for obstacle in obstacles[:]:
        obstacle[1] += current_speed

        # Check if obstacle is off screen
        if obstacle[1] > SCREEN_HEIGHT:
            obstacles.remove(obstacle)
            settings.score += 1
            settings.combo_count += 1
            check_combo()

        # Check collision with player
        elif not settings.is_invincible and (
            obstacle[1] + settings.obstacle_size > player_y and
            obstacle[1] < player_y + settings.player_size and
            obstacle[0] + settings.obstacle_size > player_x and
            obstacle[0] < player_x + settings.player_size):

            obstacles.remove(obstacle)
            settings.combo_count = 0
            settings.lives -= 1
            hit_sound.play()

            settings.last_hit_time = time.time()
            settings.is_invincible = True

            if settings.lives <= 0:
                settings.game_over = True
                game_over_sound.play()

def update_powerups():
    global player_x

    current_speed = settings.powerup_speed
    if settings.slow_time_active:
        current_speed *= 0.5

    # Update real saviors
    for savior in saviors[:]:
        savior[1] += current_speed

        if savior[1] > SCREEN_HEIGHT:
            saviors.remove(savior)
        elif (savior[1] + settings.powerup_size > player_y and
              savior[1] < player_y + settings.player_size and
              savior[0] + settings.powerup_size > player_x and
              savior[0] < player_x + settings.player_size):

            saviors.remove(savior)
            if settings.lives < settings.max_lives:
                settings.lives += 1
                life_up_sound.play()

    # Update fake saviors
    for fake in fake_saviors[:]:
        fake[1] += current_speed

        if fake[1] > SCREEN_HEIGHT:
            fake_saviors.remove(fake)
        elif (fake[1] + settings.powerup_size > player_y and
              fake[1] < player_y + settings.player_size and
              fake[0] + settings.powerup_size > player_x and
              fake[0] < player_x + settings.player_size):

            fake_saviors.remove(fake)
            settings.lives -= 1
            fake_sound.play()

            settings.last_hit_time = time.time()
            settings.is_invincible = True

            if settings.lives <= 0:
                settings.game_over = True
                game_over_sound.play()

    # Update slow time powerups
    for powerup in slow_time_powerups[:]:
        powerup[1] += current_speed

        if powerup[1] > SCREEN_HEIGHT:
            slow_time_powerups.remove(powerup)
        elif (powerup[1] + settings.powerup_size > player_y and
              powerup[1] < player_y + settings.player_size and
              powerup[0] + settings.powerup_size > player_x and
              powerup[0] < player_x + settings.player_size):

            slow_time_powerups.remove(powerup)
            settings.slow_time_active = True
            settings.slow_time_start = time.time()
            powerup_sound.play()

def check_combo():
    if settings.combo_count >= settings.combo_threshold:
        settings.score += settings.combo_bonus
        settings.combo_count = 0
        settings.show_combo = True
        settings.combo_display_time = time.time()
        combo_sound.play()

def check_status_effects(current_time):
    # Check invincibility
    if settings.is_invincible and current_time - settings.last_hit_time >= settings.invincibility_time:
        settings.is_invincible = False

    # Check slow time
    if settings.slow_time_active and current_time - settings.slow_time_start >= settings.slow_time_duration:
        settings.slow_time_active = False

    # Check combo display
    if settings.show_combo and current_time - settings.combo_display_time >= settings.combo_duration:
        settings.show_combo = False

def draw_ui(current_time):
    elapsed_time = int(current_time - settings.start_time)
    minutes = elapsed_time // 60
    seconds = elapsed_time % 60

    # Create score panel background
    score_panel = pygame.Surface((220, 160))
    score_panel.set_alpha(180)
    score_panel.fill(BLACK)
    screen.blit(score_panel, (5, 5))

    # Draw scores and stats
    texts = [
        f"🎯 Obstacles Dodged: {settings.score}",
        f"⏱️ Survival Score: {settings.survival_score}",
        f"🕒 Time: {minutes:02d}:{seconds:02d}",
        f"🚀 Speed: {settings.obstacle_speed:.1f}",
        f"⚡ Combo: {settings.combo_count}/{settings.combo_threshold}"
    ]

    for i, text in enumerate(texts):
        text_surface = text_font.render(text, True, WHITE)
        screen.blit(text_surface, (15, 15 + i * 30))

    # Create status panel background
    status_panel = pygame.Surface((250, 120))
    status_panel.set_alpha(180)
    status_panel.fill(BLACK)
    screen.blit(status_panel, (SCREEN_WIDTH - 260, 5))

    # Draw lives
    draw_lives()

    # Draw day/night indicator
    mode_text = "🌙 Night Mode" if settings.is_night_mode else "☀️ Day Mode"
    mode_display = text_font.render(mode_text, True, WHITE)
    screen.blit(mode_display, (SCREEN_WIDTH - 250, 50))

    # Draw next day/night switch countdown
    next_switch = int(settings.day_night_interval - (current_time - settings.last_day_night_switch))
    switch_text = text_font.render(f"Mode switch in: {next_switch}s", True, WHITE)
    screen.blit(switch_text, (SCREEN_WIDTH - 250, 80))

    # Draw slow time status if active
    if settings.slow_time_active:
        remaining = int(settings.slow_time_duration - (current_time - settings.slow_time_start))
        slow_text = text_font.render(f"⏳ Slow Time: {remaining}s", True, PURPLE)
        screen.blit(slow_text, (SCREEN_WIDTH - 250, 110))

def show_game_over():
    # Create a semi-transparent overlay
    if settings.game_over_overlay_alpha < 180:
        settings.game_over_overlay_alpha += 5

    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.fill(DARK_RED)
    overlay.set_alpha(settings.game_over_overlay_alpha)
    screen.blit(overlay, (0, 0))

    # Game over text
    game_over_font = pygame.font.SysFont(None, 72)
    emoji_game_over = emoji_font.render('💀 GAME OVER 💀', True, WHITE)
    # Trigger spin wheel only once
    if not settings.spin_wheel_active and not settings.spin_wheel_spinning:
        settings.spin_wheel_active = True
        settings.spin_wheel_spinning = False
        settings.spin_wheel_result = None
    text_rect = emoji_game_over.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80))
    screen.blit(emoji_game_over, text_rect)

    score_font = pygame.font.SysFont(None, 36)

    # Display scores
    texts = [
        f"Obstacles Dodged: {settings.score}",
        f"Survival Score: {settings.survival_score}",
        "Press R to restart 🔄"
    ]

    for i, text in enumerate(texts):
        text_surface = score_font.render(text, True, WHITE)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + i * 50))
        screen.blit(text_surface, text_rect)

def reset_game():
    global obstacles, saviors, fake_saviors, slow_time_powerups, player_x

    obstacles.clear()
    saviors.clear()
    fake_saviors.clear()
    slow_time_powerups.clear()

    player_x = SCREEN_WIDTH // 2 - settings.player_size // 2

    current_time = time.time()
    settings.score = 0
    settings.survival_score = 0
    settings.obstacle_speed = settings.base_obstacle_speed
    settings.start_time = current_time
    settings.last_difficulty_increase = current_time
    settings.last_savior_spawn = current_time
    settings.last_slow_time_spawn = current_time
    settings.last_day_night_switch = current_time
    settings.game_over_overlay_alpha = 0
    settings.lives = settings.max_lives
    settings.is_invincible = False
    settings.combo_count = 0
    settings.show_combo = False
    settings.slow_time_active = False
    settings.is_night_mode = False
    settings.game_over = False

# Main game loop
clock = pygame.time.Clock()

while True:
    current_time = time.time()

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Handle key presses
        if event.type == pygame.KEYDOWN:
            # Restart game
            if settings.game_over and event.key == pygame.K_r:
                reset_game()

            # Change player emoji
            if event.key == pygame.K_c and not settings.game_over:
                settings.current_emoji_index = (settings.current_emoji_index + 1) % len(settings.player_emojis)
                update_emoji_renders()

    if not settings.game_over:
        # Check status effects
        check_status_effects(current_time)

        # Increase survival score
        settings.survival_score += 1

        # Check if it's time to increase difficulty
        if current_time - settings.last_difficulty_increase >= settings.difficulty_increase_interval:
            settings.obstacle_speed += 0.5
            settings.last_difficulty_increase = current_time

        # Check if it's time to spawn a savior
        if current_time - settings.last_savior_spawn >= settings.savior_spawn_interval:
            spawn_savior()
            settings.last_savior_spawn = current_time

        # Check if it's time to spawn a slow time powerup
        if current_time - settings.last_slow_time_spawn >= settings.slow_time_interval:
            spawn_slow_time()
            settings.last_slow_time_spawn = current_time

        # Check if it's time to toggle day/night mode
        if current_time - settings.last_day_night_switch >= settings.day_night_interval:
            settings.is_night_mode = not settings.is_night_mode
            settings.last_day_night_switch = current_time

        # Get keyboard input for player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= settings.player_speed
        if keys[pygame.K_RIGHT] and player_x < SCREEN_WIDTH - settings.player_size:
            player_x += settings.player_speed

        # Randomly spawn obstacles
        if random.randint(1, settings.obstacle_spawn_rate) == 1:
            spawn_obstacle()

        # Update game objects
        update_obstacles()
        update_powerups()

        # Determine background color based on day/night mode
        bg_color = DARK_BLUE if settings.is_night_mode else BLUE
        screen.fill(bg_color)

        # Draw game objects
        draw_player()
        draw_objects()
        draw_combo()
        draw_ui(current_time)
    else:
        # Show game over screen
        show_game_over()

    # Update display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)
### 1. Emoji Storm Mode

# Add to GameSettings class:
self.emoji_storm_active = False
self.emoji_storm_start_time = 0
self.emoji_storm_duration = 10  # seconds
self.emoji_storm_trigger_time = 60  # seconds
self.storm_flash_intensity = 0

# In the main game loop:
# Check if it's time to trigger Emoji Storm
if not settings.emoji_storm_active and elapsed_time >= settings.emoji_storm_trigger_time:
    settings.emoji_storm_active = True
    settings.emoji_storm_start_time = current_time
    storm_sound.play()  # Add a storm sound effect

# Update Emoji Storm status
if settings.emoji_storm_active:
    # Calculate remaining time
    storm_remaining = settings.emoji_storm_duration - (current_time - settings.emoji_storm_start_time)

    if storm_remaining <= 0:
        settings.emoji_storm_active = False
    else:
        # Flash screen edges
        settings.storm_flash_intensity = int(time.time() * 10) % 2 * 255
        flash_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(screen, (settings.storm_flash_intensity, 0, 0), flash_rect, 5)

        # Display storm status
        storm_text = text_font.render(f"⚡ EMOJI STORM: {int(storm_remaining)}s", True, (255, 255, 0))
        screen.blit(storm_text, (SCREEN_WIDTH//2 - 100, 10))

        # Make obstacles fall faster during storm
        current_speed *= 1.5

        # Double points for dodged obstacles during storm
        # (modify the score increment in update_obstacles function)


### 2. Companion Robot Emoji

# Add to GameSettings class:
self.companion_active = True
self.companion_offset_x = 30
self.companion_offset_y = 10
self.companion_shoot_interval = 15  # seconds
self.last_companion_shoot = time.time()
self.companion_shooting = False
self.companion_shoot_start = 0
self.companion_shoot_duration = 0.5  # seconds
self.companion_target = None

# Add a function to draw the companion:
def draw_companion():
    companion_x = player_x - settings.companion_offset_x
    companion_y = player_y + settings.companion_offset_y

    # Draw companion emoji
    companion_emoji = small_emoji_font.render('🤖', True, BLACK)
    screen.blit(companion_emoji, (companion_x, companion_y))

    # Draw laser if shooting
    if settings.companion_shooting:
        if settings.companion_target:
            target_x, target_y = settings.companion_target
            pygame.draw.line(screen, (255, 0, 0),
                            (companion_x + settings.powerup_size//2, companion_y),
                            (target_x + settings.obstacle_size//2, target_y), 3)

# In the main game loop:
# Check if it's time for companion to shoot
if settings.companion_active and current_time - settings.last_companion_shoot >= settings.companion_shoot_interval:
    # Find the closest obstacle
    closest_obstacle = None
    min_distance = float('inf')

    for obstacle in obstacles:
        dist = ((obstacle[0] - player_x) ** 2 + (obstacle[1] - player_y) ** 2) ** 0.5
        if dist < min_distance:
            min_distance = dist
            closest_obstacle = obstacle

    if closest_obstacle:
        settings.companion_shooting = True
        settings.companion_shoot_start = current_time
        settings.companion_target = (closest_obstacle[0], closest_obstacle[1])
        settings.last_companion_shoot = current_time

        # Remove the targeted obstacle
        obstacles.remove(closest_obstacle)
        laser_sound.play()  # Add a laser sound effect

# Update companion shooting status
if settings.companion_shooting:
    if current_time - settings.companion_shoot_start >= settings.companion_shoot_duration:
        settings.companion_shooting = False
        settings.companion_target = None


### 3. Game Over Spin Wheel

# Add to GameSettings class:
self.spin_wheel_active = False
self.spin_wheel_spinning = False
self.spin_wheel_result = None
self.spin_wheel_options = ["Retry", "Retry +1 Life", "Exit"]
self.spin_wheel_angle = 0
self.spin_wheel_speed = 0
self.spin_wheel_deceleration = 0.2
self.spin_start_time = 0

# Add a function to draw the spin wheel:
def draw_spin_wheel():
    # Draw wheel background
    wheel_center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
    wheel_radius = 100
    pygame.draw.circle(screen, WHITE, wheel_center, wheel_radius)
    pygame.draw.circle(screen, BLACK, wheel_center, wheel_radius, 3)

    # Draw wheel sections
    colors = [(255, 200, 200), (200, 255, 200), (200, 200, 255)]
    for i in range(3):
        start_angle = i * 120
        end_angle = (i + 1) * 120
        pygame.draw.arc(screen, colors[i],
                       (wheel_center[0] - wheel_radius, wheel_center[1] - wheel_radius,
                        wheel_radius * 2, wheel_radius * 2),
                       math.radians(start_angle), math.radians(end_angle), wheel_radius)

    # Draw options text
    for i, option in enumerate(settings.spin_wheel_options):
        angle = math.radians(i * 120 + 60 - settings.spin_wheel_angle)
        text_x = wheel_center[0] + int(wheel_radius * 0.7 * math.cos(angle))
        text_y = wheel_center[1] + int(wheel_radius * 0.7 * math.sin(angle))

        option_text = text_font.render(option, True, BLACK)
        text_rect = option_text.get_rect(center=(text_x, text_y))
        screen.blit(option_text, text_rect)

    # Draw pointer
    pointer_points = [(wheel_center[0], wheel_center[1] - wheel_radius - 20),
                     (wheel_center[0] - 10, wheel_center[1] - wheel_radius),
                     (wheel_center[0] + 10, wheel_center[1] - wheel_radius)]
    pygame.draw.polygon(screen, RED, pointer_points)

    # Draw spin instruction
    if not settings.spin_wheel_spinning:
        spin_text = text_font.render("Press SPACE to spin!", True, WHITE)
        screen.blit(spin_text, (wheel_center[0] - 80, wheel_center[1] + wheel_radius + 30))

# In the game over section:
if settings.game_over:
    if not settings.spin_wheel_active:
        show_game_over()

        # Show "Press SPACE to continue" text
        continue_text = text_font.render("Press SPACE to continue", True, WHITE)
        text_rect = continue_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 150))
        screen.blit(continue_text, text_rect)

        # Check for SPACE key to activate spin wheel
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            settings.spin_wheel_active = True
    else:
        # Draw spin wheel
        draw_spin_wheel()

        # Handle spinning logic
        if settings.spin_wheel_spinning:
            # Decelerate the wheel
            settings.spin_wheel_speed -= settings.spin_wheel_deceleration
            if settings.spin_wheel_speed <= 0:
                settings.spin_wheel_speed = 0
                settings.spin_wheel_spinning = False

                # Determine result based on final angle
                final_section = int((settings.spin_wheel_angle % 360) / 120)
                settings.spin_wheel_result = settings.spin_wheel_options[final_section]

                # Handle result
                if settings.spin_wheel_result == "Retry":
                    reset_game()
                elif settings.spin_wheel_result == "Retry +1 Life":
                    reset_game()
                    settings.lives += 1
                elif settings.spin_wheel_result == "Exit":
                    pygame.quit()
                    sys.exit()

            # Update wheel angle
            settings.spin_wheel_angle += settings.spin_wheel_speed
        else:
            # Check for SPACE key to spin the wheel
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] and not settings.spin_wheel_result:
                settings.spin_wheel_spinning = True
                settings.spin_wheel_speed = random.uniform(10, 20)
                settings.spin_start_time = current_time


### 4. Wind Effect

# Add to GameSettings class:
self.wind_active = False
self.wind_direction = 0  # -1 for left, 1 for right
self.wind_start_time = 0
self.wind_duration = 5  # seconds
self.wind_strength = 2  # pixels per frame
self.wind_warning_shown = False
self.wind_warning_time = 0
self.wind_warning_duration = 2  # seconds
self.next_wind_time = random.uniform(25, 40)

# In the main game loop:
# Check if it's time to trigger wind
if not settings.wind_active and not settings.wind_warning_shown and elapsed_time >= settings.next_wind_time:
    settings.wind_warning_shown = True
    settings.wind_warning_time = current_time
    settings.wind_direction = random.choice([-1, 1])

# Show wind warning
if settings.wind_warning_shown and not settings.wind_active:
    warning_time = current_time - settings.wind_warning_time

    if warning_time <= settings.wind_warning_duration:
        # Flash warning text
        if int(warning_time * 4) % 2 == 0:
            direction_text = "LEFT" if settings.wind_direction < 0 else "RIGHT"
            warning_text = text_font.render(f"WIND WARNING! ({direction_text})", True, (255, 255, 0))
            text_rect = warning_text.get_rect(center=(SCREEN_WIDTH//2, 50))
            screen.blit(warning_text, text_rect)
    else:
        settings.wind_warning_shown = False
        settings.wind_active = True
        settings.wind_start_time = current_time

# Update wind status
if settings.wind_active:
    wind_remaining = settings.wind_duration - (current_time - settings.wind_start_time)

    if wind_remaining <= 0:
        settings.wind_active = False
        settings.next_wind_time = elapsed_time + random.uniform(25, 40)
    else:
        # Display wind indicator
        direction_text = "←" if settings.wind_direction < 0 else "→"
        wind_text = text_font.render(f"WIND {direction_text} {int(wind_remaining)}s", True, (200, 200, 255))
        screen.blit(wind_text, (SCREEN_WIDTH//2 - 50, 10))

        # Draw wind particles
        for _ in range(10):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            length = random.randint(5, 15)
            pygame.draw.line(screen, (200, 200, 255),
                            (x, y),
                            (x + length * settings.wind_direction, y),
                            1)

        # Apply wind effect to obstacles
        for obstacle in obstacles:
            obstacle[0] += settings.wind_strength * settings.wind_direction


### 5. Player Emoji Chat Bubbles
# Add to GameSettings class:
self.chat_bubble_active = False
self.chat_bubble_text = ""
self.chat_bubble_start = 0
self.chat_bubble_duration = 2  # seconds

# Add a function to show chat bubble:
def show_chat_bubble(text):
    settings.chat_bubble_active = True
    settings.chat_bubble_text = text
    settings.chat_bubble_start = time.time()

# Add a function to draw chat bubble:
def draw_chat_bubble():
    if settings.chat_bubble_active:
        bubble_time = time.time() - settings.chat_bubble_start

        if bubble_time <= settings.chat_bubble_duration:
            bubble_emoji = emoji_font.render(settings.chat_bubble_text, True, BLACK)

            # Position bubble above player
            bubble_x = player_x + settings.player_size//2 - bubble_emoji.get_width()//2
            bubble_y = player_y - bubble_emoji.get_height() - 5

            # Draw bubble background
            bubble_rect = bubble_emoji.get_rect(topleft=(bubble_x-5, bubble_y-5))
            bubble_rect.width += 10
            bubble_rect.height += 10
            pygame.draw.ellipse(screen, WHITE, bubble_rect)
            pygame.draw.ellipse(screen, BLACK, bubble_rect, 2)

            # Draw bubble pointer
            pointer_points = [(player_x + settings.player_size//2, player_y),
                             (player_x + settings.player_size//2 - 10, bubble_y + bubble_emoji.get_height()),
                             (player_x + settings.player_size//2 + 10, bubble_y + bubble_emoji.get_height())]
            pygame.draw.polygon(screen, WHITE, pointer_points)
            pygame.draw.polygon(screen, BLACK, pointer_points, 2)

            # Draw bubble text
            screen.blit(bubble_emoji, (bubble_x, bubble_y))
        else:
            settings.chat_bubble_active = False

# Modify the collision detection to show chat bubble when hit:
if not settings.is_invincible and collision_detected:
    # ... existing collision code ...
    show_chat_bubble("😱")

# Modify the power-up collection to show chat bubble:
if power_up_collected:
    # ... existing power-up code ...
    show_chat_bubble("💪")

import pygame
import sys
import random
import time
import os
import math

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Emoji Dodge Game Ultimate")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 128, 0)
BLUE = (100, 149, 237)  # Day background
DARK_BLUE = (25, 25, 112)  # Night background
DARK_RED = (139, 0, 0)
GOLD = (255, 215, 0)
PURPLE = (128, 0, 128)

# Create sounds directory
sounds_dir = os.path.join(os.path.dirname(__file__), "sounds")
os.makedirs(sounds_dir, exist_ok=True)

# Sound management
def create_sound(name):
    path = os.path.join(sounds_dir, f"{name}.wav")
    if not os.path.exists(path):
        with open(path, 'wb') as f:
            f.write(b'')
    try:
        return pygame.mixer.Sound(path)
    except:
        class DummySound:
            def play(self): pass
        return DummySound()

# Load sounds
hit_sound = create_sound("hit")
game_over_sound = create_sound("game_over")
life_up_sound = create_sound("life_up")
combo_sound = create_sound("combo")
powerup_sound = create_sound("powerup")
fake_sound = create_sound("fake")
storm_sound = create_sound("storm")
laser_sound = create_sound("laser")
wind_sound = create_sound("wind")
spin_sound = create_sound("spin")

# Game settings
class GameSettings:
    def __init__(self):
        # Player settings
        self.player_size = 50
        self.player_speed = 8
        self.player_emojis = ['😎', '🐱', '🦸‍♂️']
        self.current_emoji_index = 0

        # Lives system
        self.max_lives = 3
        self.lives = self.max_lives
        self.invincibility_time = 1.5
        self.is_invincible = False
        self.last_hit_time = 0

        # Combo system
        self.combo_count = 0
        self.combo_threshold = 10
        self.combo_bonus = 50
        self.show_combo = False
        self.combo_display_time = 0
        self.combo_duration = 3

        # Day/Night cycle
        self.is_night_mode = False
        self.day_night_interval = 30
        self.last_day_night_switch = time.time()

        # Obstacle settings
        self.obstacle_size = 40
        self.base_obstacle_speed = 5
        self.obstacle_speed = self.base_obstacle_speed
        self.obstacle_spawn_rate = 30

        # Powerup settings
        self.powerup_size = 40
        self.powerup_speed = 3
        self.savior_spawn_interval = 15
        self.last_savior_spawn = time.time()

        # Slow time powerup
        self.slow_time_active = False
        self.slow_time_start = 0
        self.slow_time_duration = 5
        self.slow_time_interval = 20
        self.last_slow_time_spawn = time.time()

        # Emoji Storm mode
        self.emoji_storm_active = False
        self.emoji_storm_start_time = 0
        self.emoji_storm_duration = 10
        self.emoji_storm_trigger_time = 60
        self.storm_flash_intensity = 0

        # Companion robot
        self.companion_active = True
        self.companion_offset_x = 30
        self.companion_offset_y = 10
        self.companion_shoot_interval = 15
        self.last_companion_shoot = time.time()
        self.companion_shooting = False
        self.companion_shoot_start = 0
        self.companion_shoot_duration = 0.5
        self.companion_target = None

        # Wind effect
        self.wind_active = False
        self.wind_direction = 0  # -1 for left, 1 for right
        self.wind_start_time = 0
        self.wind_duration = 5
        self.wind_strength = 2
        self.wind_warning_shown = False
        self.wind_warning_time = 0
        self.wind_warning_duration = 2
        self.next_wind_time = random.uniform(25, 40)

        # Chat bubble
        self.chat_bubble_active = False
        self.chat_bubble_text = ""
        self.chat_bubble_start = 0
        self.chat_bubble_duration = 2

        # Spin wheel
        self.spin_wheel_active = False
        self.spin_wheel_spinning = False
        self.spin_wheel_result = None
        self.spin_wheel_options = ["Retry", "Retry +1 Life", "Exit"]
        self.spin_wheel_angle = 0
        self.spin_wheel_speed = 0
        self.spin_wheel_deceleration = 0.2
        self.spin_start_time = 0

        # Game state
        self.score = 0
        self.survival_score = 0
        self.game_over = False
        self.game_over_overlay_alpha = 0

        # Timer for increasing difficulty
        self.start_time = time.time()
        self.last_difficulty_increase = self.start_time
        self.difficulty_increase_interval = 10

# Initialize game settings
settings = GameSettings()

# Player position
player_x = SCREEN_WIDTH // 2 - settings.player_size // 2
player_y = SCREEN_HEIGHT - settings.player_size - 10

# Game objects
obstacles = []
saviors = []
fake_saviors = []
slow_time_powerups = []

# Font for emoji
emoji_font = pygame.font.SysFont('segoe ui emoji', settings.player_size)
small_emoji_font = pygame.font.SysFont('segoe ui emoji', settings.obstacle_size)
text_font = pygame.font.SysFont(None, 28)
large_font = pygame.font.SysFont(None, 48)

# Emoji renders
def update_emoji_renders():
    global player_emoji, heart_emoji, savior_emoji, fake_savior_emoji, slow_time_emoji, companion_emoji, obstacle_emojis

    player_emoji = emoji_font.render(settings.player_emojis[settings.current_emoji_index], True, BLACK)
    heart_emoji = small_emoji_font.render('❤️', True, BLACK)
    savior_emoji = small_emoji_font.render('🛡️', True, BLACK)
    fake_savior_emoji = small_emoji_font.render('💔', True, BLACK)
    slow_time_emoji = small_emoji_font.render('⏳', True, BLACK)
    companion_emoji = small_emoji_font.render('🤖', True, BLACK)

    obstacle_emojis = [
        small_emoji_font.render('🔥', True, BLACK),
        small_emoji_font.render('💣', True, BLACK),
        small_emoji_font.render('🪨', True, BLACK),
        small_emoji_font.render('⚡', True, BLACK),
        small_emoji_font.render('🌪️', True, BLACK)
    ]

# Initialize emoji renders
update_emoji_renders()

# Game functions
def draw_player():
    if settings.is_invincible and int(time.time() * 10) % 2 == 0:
        return  # Flash effect when invincible
    screen.blit(player_emoji, (player_x, player_y))

def draw_companion():
    companion_x = player_x - settings.companion_offset_x
    companion_y = player_y + settings.companion_offset_y

    # Draw companion emoji
    screen.blit(companion_emoji, (companion_x, companion_y))

    # Draw laser if shooting
    if settings.companion_shooting:
        if settings.companion_target:
            target_x, target_y = settings.companion_target
            pygame.draw.line(screen, (255, 0, 0),
                            (companion_x + settings.powerup_size//2, companion_y),
                            (target_x + settings.obstacle_size//2, target_y), 3)

def spawn_obstacle():
    x = random.randint(0, SCREEN_WIDTH - settings.obstacle_size)
    y = -settings.obstacle_size
    emoji = random.choice(obstacle_emojis)
    obstacles.append([x, y, emoji])

def spawn_savior():
    x = random.randint(0, SCREEN_WIDTH - settings.powerup_size)
    y = -settings.powerup_size

    # 1 in 4 chance to spawn a fake savior
    if random.randint(1, 4) == 1:
        fake_saviors.append([x, y])
    else:
        saviors.append([x, y])

def spawn_slow_time():
    x = random.randint(0, SCREEN_WIDTH - settings.powerup_size)
    y = -settings.powerup_size
    slow_time_powerups.append([x, y])

def draw_objects():
    # Draw obstacles
    for obstacle in obstacles:
        screen.blit(obstacle[2], (obstacle[0], obstacle[1]))

    # Draw real saviors
    for savior in saviors:
        glow_rect = pygame.Rect(savior[0]-5, savior[1]-5, settings.powerup_size+10, settings.powerup_size+10)
        pygame.draw.ellipse(screen, GOLD, glow_rect)
        screen.blit(savior_emoji, (savior[0], savior[1]))

    # Draw fake saviors
    for fake in fake_saviors:
        glow_rect = pygame.Rect(fake[0]-5, fake[1]-5, settings.powerup_size+10, settings.powerup_size+10)
        pygame.draw.ellipse(screen, RED, glow_rect)
        screen.blit(fake_savior_emoji, (fake[0], fake[1]))

    # Draw slow time powerups
    for powerup in slow_time_powerups:
        glow_rect = pygame.Rect(powerup[0]-5, powerup[1]-5, settings.powerup_size+10, settings.powerup_size+10)
        pygame.draw.ellipse(screen, PURPLE, glow_rect)
        screen.blit(slow_time_emoji, (powerup[0], powerup[1]))

def draw_lives():
    for i in range(settings.lives):
        screen.blit(heart_emoji, (SCREEN_WIDTH - 50 - i * 35, 15))

def draw_combo():
    if settings.show_combo:
        combo_text = emoji_font.render(f"+{settings.combo_bonus} COMBO! ⚡", True, GOLD)
        text_rect = combo_text.get_rect(center=(SCREEN_WIDTH//2, 100))
        screen.blit(combo_text, text_rect)

def draw_chat_bubble():
    if settings.chat_bubble_active:
        bubble_time = time.time() - settings.chat_bubble_start

        if bubble_time <= settings.chat_bubble_duration:
            bubble_emoji = emoji_font.render(settings.chat_bubble_text, True, BLACK)

            # Position bubble above player
            bubble_x = player_x + settings.player_size//2 - bubble_emoji.get_width()//2
            bubble_y = player_y - bubble_emoji.get_height() - 5

            # Draw bubble background
            bubble_rect = bubble_emoji.get_rect(topleft=(bubble_x-5, bubble_y-5))
            bubble_rect.width += 10
            bubble_rect.height += 10
            pygame.draw.ellipse(screen, WHITE, bubble_rect)
            pygame.draw.ellipse(screen, BLACK, bubble_rect, 2)

            # Draw bubble pointer
            pointer_points = [(player_x + settings.player_size//2, player_y),
                             (player_x + settings.player_size//2 - 10, bubble_y + bubble_emoji.get_height()),
                             (player_x + settings.player_size//2 + 10, bubble_y + bubble_emoji.get_height())]
            pygame.draw.polygon(screen, WHITE, pointer_points)
            pygame.draw.polygon(screen, BLACK, pointer_points, 2)

            # Draw bubble text
            screen.blit(bubble_emoji, (bubble_x, bubble_y))
        else:
            settings.chat_bubble_active = False

def show_chat_bubble(text):
    settings.chat_bubble_active = True
    settings.chat_bubble_text = text
    settings.chat_bubble_start = time.time()

def update_obstacles():
    global obstacles

    current_speed = settings.obstacle_speed

    # Apply modifiers
    if settings.slow_time_active:
        current_speed *= 0.5  # 50% slower when slow time is active
    if settings.emoji_storm_active:
        current_speed *= 1.5  # 50% faster during emoji storm

    for obstacle in obstacles[:]:
        # Apply wind effect
        if settings.wind_active:
            obstacle[0] += settings.wind_strength * settings.wind_direction

        # Move obstacle down
        obstacle[1] += current_speed

        # Check if obstacle is off screen
        if obstacle[1] > SCREEN_HEIGHT:
            obstacles.remove(obstacle)

            # Award points
            point_value = 1
            if settings.emoji_storm_active:
                point_value *= 2  # Double points during emoji storm

            settings.score += point_value
            settings.combo_count += 1
            check_combo()

        # Check collision with player if not invincible
        elif not settings.is_invincible and (
            obstacle[1] + settings.obstacle_size > player_y and
            obstacle[1] < player_y + settings.player_size and
            obstacle[0] + settings.obstacle_size > player_x and
            obstacle[0] < player_x + settings.player_size):

            obstacles.remove(obstacle)
            settings.combo_count = 0
            settings.lives -= 1
            hit_sound.play()

            # Show scared emoji
            show_chat_bubble("😱")

            settings.last_hit_time = time.time()
            settings.is_invincible = True

            if settings.lives <= 0:
                settings.game_over = True
                game_over_sound.play()

def update_powerups():
    global player_x

    current_speed = settings.powerup_speed
    if settings.slow_time_active:
        current_speed *= 0.5

    # Update real saviors
    for savior in saviors[:]:
        savior[1] += current_speed

        if savior[1] > SCREEN_HEIGHT:
            saviors.remove(savior)
        elif (savior[1] + settings.powerup_size > player_y and
              savior[1] < player_y + settings.player_size and
              savior[0] + settings.powerup_size > player_x and
              savior[0] < player_x + settings.player_size):

            saviors.remove(savior)
            if settings.lives < settings.max_lives:
                settings.lives += 1
                life_up_sound.play()
                show_chat_bubble("💪")

    # Update fake saviors
    for fake in fake_saviors[:]:
        fake[1] += current_speed

        if fake[1] > SCREEN_HEIGHT:
            fake_saviors.remove(fake)
        elif (fake[1] + settings.powerup_size > player_y and
              fake[1] < player_y + settings.player_size and
              fake[0] + settings.powerup_size > player_x and
              fake[0] < player_x + settings.player_size):

            fake_saviors.remove(fake)
            settings.lives -= 1
            fake_sound.play()
            show_chat_bubble("😱")

            settings.last_hit_time = time.time()
            settings.is_invincible = True

            if settings.lives <= 0:
                settings.game_over = True
                game_over_sound.play()

    # Update slow time powerups
    for powerup in slow_time_powerups[:]:
        powerup[1] += current_speed

        if powerup[1] > SCREEN_HEIGHT:
            slow_time_powerups.remove(powerup)
        elif (powerup[1] + settings.powerup_size > player_y and
              powerup[1] < player_y + settings.player_size and
              powerup[0] + settings.powerup_size > player_x and
              powerup[0] < player_x + settings.player_size):

            slow_time_powerups.remove(powerup)
            settings.slow_time_active = True
            settings.slow_time_start = time.time()
            powerup_sound.play()
            show_chat_bubble("⏳")

def update_companion(current_time):
    # Check if it's time for companion to shoot
    if settings.companion_active and current_time - settings.last_companion_shoot >= settings.companion_shoot_interval:
        # Find the closest obstacle
        closest_obstacle = None
        min_distance = float('inf')

        for obstacle in obstacles:
            dist = ((obstacle[0] - player_x) ** 2 + (obstacle[1] - player_y) ** 2) ** 0.5
            if dist < min_distance:
                min_distance = dist
                closest_obstacle = obstacle

        if closest_obstacle:
            settings.companion_shooting = True
            settings.companion_shoot_start = current_time
            settings.companion_target = (closest_obstacle[0], closest_obstacle[1])
            settings.last_companion_shoot = current_time

            # Remove the targeted obstacle
            obstacles.remove(closest_obstacle)
            laser_sound.play()
            settings.score += 1  # Award a point for the destroyed obstacle

    # Update companion shooting status
    if settings.companion_shooting:
        if current_time - settings.companion_shoot_start >= settings.companion_shoot_duration:
            settings.companion_shooting = False
            settings.companion_target = None

def check_combo():
    if settings.combo_count >= settings.combo_threshold:
        settings.score += settings.combo_bonus
        settings.combo_count = 0
        settings.show_combo = True
        settings.combo_display_time = time.time()
        combo_sound.play()

def check_status_effects(current_time):
    # Check invincibility
    if settings.is_invincible and current_time - settings.last_hit_time >= settings.invincibility_time:
        settings.is_invincible = False

    # Check slow time
    if settings.slow_time_active and current_time - settings.slow_time_start >= settings.slow_time_duration:
        settings.slow_time_active = False

    # Check combo display
    if settings.show_combo and current_time - settings.combo_display_time >= settings.combo_duration:
        settings.show_combo = False

    # Check emoji storm
    if settings.emoji_storm_active and current_time - settings.emoji_storm_start_time >= settings.emoji_storm_duration:
        settings.emoji_storm_active = False

def draw_spin_wheel():
    # Draw wheel background
    wheel_center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
    wheel_radius = 100
    pygame.draw.circle(screen, WHITE, wheel_center, wheel_radius)
    pygame.draw.circle(screen, BLACK, wheel_center, wheel_radius, 3)

    # Draw wheel sections
    colors = [(255, 200, 200), (200, 255, 200), (200, 200, 255)]
    for i in range(3):
        start_angle = i * 120
        end_angle = (i + 1) * 120
        pygame.draw.arc(screen, colors[i],
                       (wheel_center[0] - wheel_radius, wheel_center[1] - wheel_radius,
                        wheel_radius * 2, wheel_radius * 2),
                       math.radians(start_angle), math.radians(end_angle), wheel_radius)

    # Draw options text
    for i, option in enumerate(settings.spin_wheel_options):
        angle = math.radians(i * 120 + 60 - settings.spin_wheel_angle)
        text_x = wheel_center[0] + int(wheel_radius * 0.7 * math.cos(angle))
        text_y = wheel_center[1] + int(wheel_radius * 0.7 * math.sin(angle))

        option_text = text_font.render(option, True, BLACK)
        text_rect = option_text.get_rect(center=(text_x, text_y))
        screen.blit(option_text, text_rect)

    # Draw pointer
    pointer_points = [(wheel_center[0], wheel_center[1] - wheel_radius - 20),
                     (wheel_center[0] - 10, wheel_center[1] - wheel_radius),
                     (wheel_center[0] + 10, wheel_center[1] - wheel_radius)]
    pygame.draw.polygon(screen, RED, pointer_points)

    # Draw spin instruction
    if not settings.spin_wheel_spinning:
        spin_text = text_font.render("Press SPACE to spin!", True, WHITE)
        screen.blit(spin_text, (wheel_center[0] - 80, wheel_center[1] + wheel_radius + 30))

def draw_ui(current_time):
    elapsed_time = int(current_time - settings.start_time)
    minutes = elapsed_time // 60
    seconds = elapsed_time % 60

    # Create score panel background
    score_panel = pygame.Surface((220, 160))
    score_panel.set_alpha(180)
    score_panel.fill(BLACK)
    screen.blit(score_panel, (5, 5))

    # Draw scores and stats
    texts = [
        f"🎯 Obstacles Dodged: {settings.score}",
        f"⏱️ Survival Score: {settings.survival_score}",
        f"🕒 Time: {minutes:02d}:{seconds:02d}",
        f"🚀 Speed: {settings.obstacle_speed:.1f}",
        f"⚡ Combo: {settings.combo_count}/{settings.combo_threshold}"
    ]

    for i, text in enumerate(texts):
        text_surface = text_font.render(text, True, WHITE)
        screen.blit(text_surface, (15, 15 + i * 30))

    # Create status panel background
    status_panel = pygame.Surface((250, 120))
    status_panel.set_alpha(180)
    status_panel.fill(BLACK)
    screen.blit(status_panel, (SCREEN_WIDTH - 260, 5))

    # Draw lives
    draw_lives()

    # Draw day/night indicator
    mode_text = "🌙 Night Mode" if settings.is_night_mode else "☀️ Day Mode"
    mode_display = text_font.render(mode_text, True, WHITE)
    screen.blit(mode_display, (SCREEN_WIDTH - 250, 50))

    # Draw next day/night switch countdown
    next_switch = int(settings.day_night_interval - (current_time - settings.last_day_night_switch))
    switch_text = text_font.render(f"Mode switch in: {next_switch}s", True, WHITE)
    screen.blit(switch_text, (SCREEN_WIDTH - 250, 80))

    # Draw slow time status if active
    if settings.slow_time_active:
        remaining = int(settings.slow_time_duration - (current_time - settings.slow_time_start))
        slow_text = text_font.render(f"⏳ Slow Time: {remaining}s", True, PURPLE)
        screen.blit(slow_text, (SCREEN_WIDTH - 250, 110))

    # Draw companion cooldown
    companion_cooldown = int(settings.companion_shoot_interval - (current_time - settings.last_companion_shoot))
    if companion_cooldown > 0:
        companion_text = text_font.render(f"🤖 Laser in: {companion_cooldown}s", True, WHITE)
        screen.blit(companion_text, (SCREEN_WIDTH - 250, 140))

    # Draw emoji storm indicator if active
    if settings.emoji_storm_active:
        storm_remaining = int(settings.emoji_storm_duration - (current_time - settings.emoji_storm_start_time))
        storm_text = large_font.render(f"⚡ EMOJI STORM: {storm_remaining}s ⚡", True, (255, 255, 0))
        text_rect = storm_text.get_rect(center=(SCREEN_WIDTH//2, 30))
        screen.blit(storm_text, text_rect)

        # Flash screen edges
        settings.storm_flash_intensity = int(time.time() * 10) % 2 * 255
        flash_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(screen, (settings.storm_flash_intensity, 0, 0), flash_rect, 5)

    # Draw wind warning
    if settings.wind_warning_shown and not settings.wind_active:
        warning_time = current_time - settings.wind_warning_time

        if warning_time <= settings.wind_warning_duration:
            # Flash warning text
            if int(warning_time * 4) % 2 == 0:
                direction_text = "LEFT" if settings.wind_direction < 0 else "RIGHT"
                warning_text = large_font.render(f"WIND WARNING! ({direction_text})", True, (255, 255, 0))
                text_rect = warning_text.get_rect(center=(SCREEN_WIDTH//2, 50))
                screen.blit(warning_text, text_rect)

    # Draw wind effect
    if settings.wind_active:
        wind_remaining = int(settings.wind_duration - (current_time - settings.wind_start_time))
        direction_text = "←" if settings.wind_direction < 0 else "→"
        wind_text = text_font.render(f"WIND {direction_text} {wind_remaining}s", True, (200, 200, 255))
        screen.blit(wind_text, (SCREEN_WIDTH//2 - 50, 10))

        # Draw wind particles
        for _ in range(10):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            length = random.randint(5, 15)
            pygame.draw.line(screen, (200, 200, 255),
                            (x, y),
                            (x + length * settings.wind_direction, y),
                            1)

def show_game_over():
    # Create a semi-transparent overlay
    if settings.game_over_overlay_alpha < 180:
        settings.game_over_overlay_alpha += 5

    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.fill(DARK_RED)
    overlay.set_alpha(settings.game_over_overlay_alpha)
    screen.blit(overlay, (0, 0))

    # Game over text
    game_over_font = pygame.font.SysFont(None, 72)
    emoji_game_over = emoji_font.render('💀 GAME OVER 💀', True, WHITE)
    text_rect = emoji_game_over.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80))
    screen.blit(emoji_game_over, text_rect)

    score_font = pygame.font.SysFont(None, 36)

    # Display scores
    texts = [
        f"Obstacles Dodged: {settings.score}",
        f"Survival Score: {settings.survival_score}",
        "Press SPACE to continue"
    ]

    for i, text in enumerate(texts):
        text_surface = score_font.render(text, True, WHITE)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + i * 50))
        screen.blit(text_surface, text_rect)

def reset_game(extra_life=False):
    global obstacles, saviors, fake_saviors, slow_time_powerups, player_x

    obstacles.clear()
    saviors.clear()
    fake_saviors.clear()
    slow_time_powerups.clear()

    player_x = SCREEN_WIDTH // 2 - settings.player_size // 2

    current_time = time.time()
    settings.score = 0
    settings.survival_score = 0
    settings.obstacle_speed = settings.base_obstacle_speed
    settings.start_time = current_time
    settings.last_difficulty_increase = current_time
    settings.last_savior_spawn = current_time
    settings.last_slow_time_spawn = current_time
    settings.last_day_night_switch = current_time
    settings.last_companion_shoot = current_time
    settings.game_over_overlay_alpha = 0
    settings.lives = settings.max_lives + (1 if extra_life else 0)
    settings.is_invincible = False
    settings.companion_shooting = False
    settings.companion_target = None
    settings.combo_count = 0
    settings.show_combo = False
    settings.slow_time_active = False
    settings.emoji_storm_active = False
    settings.wind_active = False
    settings.wind_warning_shown = False
    settings.next_wind_time = random.uniform(25, 40)
    settings.chat_bubble_active = False
    settings.is_night_mode = False
    settings.game_over = False
    settings.spin_wheel_active = False
    settings.spin_wheel_spinning = False
    settings.spin_wheel_result = None

# Main game loop
clock = pygame.time.Clock()

while True:
    current_time = time.time()
    elapsed_time = int(current_time - settings.start_time)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Handle key presses
        if event.type == pygame.KEYDOWN:
            # Change player emoji
            if event.key == pygame.K_c and not settings.game_over:
                settings.current_emoji_index = (settings.current_emoji_index + 1) % len(settings.player_emojis)
