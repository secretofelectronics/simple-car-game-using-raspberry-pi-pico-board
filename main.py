from machine import Pin, I2C
import time
import urandom
from i2c_lcd import I2cLcd

# I2C setup
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
lcd = I2cLcd(i2c, 0x27, 2, 16)  # Change address if needed

# Button setup
button_pin = Pin(2, Pin.IN, Pin.PULL_UP)

# Game variables
car_row = 0  # Car's initial row (0 or 1)
obstacle_pos_top = 15  # Initial obstacle position for top row
obstacle_pos_bottom = 10  # Initial obstacle position for bottom row
score = 0
game_over = False
last_update = time.ticks_ms()
speed = 200  # Initial speed (lower is faster)
min_speed = 50  # Minimum speed
speed_increase_interval = 5000  # Interval to increase speed (in milliseconds)
last_speed_increase = time.ticks_ms()

# Function to display the game
def display_game():
    lcd.clear()
    
    # Display car at fixed column 0 on the current row
    lcd.move_to(0, car_row)
    lcd.putstr('>')  # Player car symbol
    
    # Display obstacles
    lcd.move_to(obstacle_pos_top, 0)
    lcd.putstr('<')  # Obstacle car symbol for top row
    
    lcd.move_to(obstacle_pos_bottom, 1)
    lcd.putstr('<')  # Obstacle car symbol for bottom row

# Function to display the game over message
def display_game_over():
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("Game Over!")
    lcd.move_to(0, 1)
    lcd.putstr(f"Score: {score}")

# Function to toggle car's row position
def toggle_car_row():
    global car_row
    car_row = 1 - car_row  # Toggle between 0 and 1

# Function to update game state
def update_game():
    global obstacle_pos_top, obstacle_pos_bottom, score, game_over
    
    # Move top obstacle
    obstacle_pos_top -= 1
    if obstacle_pos_top < 0:
        obstacle_pos_top = 15
        if urandom.getrandbits(2) == 0:
            obstacle_pos_top += urandom.randint(5, 10)  # Add randomness to obstacle position
        score += 1  # Increase score when a new obstacle appears

    # Move bottom obstacle
    obstacle_pos_bottom -= 1
    if obstacle_pos_bottom < 0:
        # Ensure that the new position for the bottom obstacle is not the same as the top obstacle
        obstacle_pos_bottom = 15
        if urandom.getrandbits(2) == 0:
            obstacle_pos_bottom += urandom.randint(5, 10)  # Add randomness to obstacle position
        score += 1  # Increase score when a new obstacle appears

    # Check for collision
    if (obstacle_pos_top == 0 and car_row == 0) or (obstacle_pos_bottom == 0 and car_row == 1):
        game_over = True

# Function to restart the game
def restart_game():
    global game_over, score, speed, obstacle_pos_top, obstacle_pos_bottom, last_update, last_speed_increase, car_row
    game_over = False
    score = 0
    speed = 200
    obstacle_pos_top = 15
    obstacle_pos_bottom = 10
    car_row = 0
    last_update = time.ticks_ms()
    last_speed_increase = time.ticks_ms()
    lcd.clear()

# Welcome message
lcd.move_to(0, 0)
lcd.putstr("Car Game")
time.sleep(2)
lcd.clear()

while True:
    button_state = not button_pin.value()
    
    # Restart the game if it's over and the button is pressed
    if game_over and button_state:
        restart_game()
    
    # Toggle car's row position on button press
    if not game_over and button_state:
        toggle_car_row()
    
    # Update the game state at regular intervals
    if not game_over and time.ticks_diff(time.ticks_ms(), last_update) > speed:
        last_update = time.ticks_ms()
        update_game()
    
    # Increase the speed at regular intervals
    if not game_over and time.ticks_diff(time.ticks_ms(), last_speed_increase) > speed_increase_interval:
        last_speed_increase = time.ticks_ms()
        if speed > min_speed:
            speed -= 10  # Increase the speed (lower the speed value)
    
    # Display the game or game over message
    if game_over:
        display_game_over()
    else:
        display_game()
    
    time.sleep(0.1)  # Adjust speed as needed