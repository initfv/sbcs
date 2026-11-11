import random

NUM_RIVALS = 1
LANE_COUNT = NUM_RIVALS + 1
LANE_WIDTH = 110
ROAD_WIDTH = LANE_WIDTH * LANE_COUNT
SHOULDER_WIDTH = 55
PLAYER_ROW = 480
MAX_SPEED = 10000
SHOULDER_MAX_SPEED = MAX_SPEED * 0.7
ROUGH_MAX_SPEED = MAX_SPEED * 0.4
ACCEL = 0.12
BRAKE = 0.35
COAST = 0.04
ROUGH_BRAKE = 0.40

DASH_PERIOD = 60
DASH_LENGTH = 30

# >>>>>>>>>>>>>>>>>>>>>>
# NEW (not in Week 2): how far away the finish line is
FINISH_DISTANCE = 3900
# <<<<<<<<<<<<<<<<<<<<<<

RIVAL_COLORS = ["car_blue", "car_green", "car_yellow"]

GRASS_MARGIN = 200
WIDTH = ROAD_WIDTH + 2 * SHOULDER_WIDTH + 2 * GRASS_MARGIN
HEIGHT = 600

GRASS = (40, 120, 55)
GRAVEL = (150, 140, 110)
TARMAC = (60, 60, 68)
LINE = (240, 240, 240)

player = Actor("car_red", (WIDTH // 2, PLAYER_ROW))
player_speed = 0.0
distance_traveled = 0.0
game_state = "racing"


def road_center_x(y):
    return WIDTH // 2


def road_left(y):
    return road_center_x(y) - ROAD_WIDTH // 2


def road_right(y):
    return road_center_x(y) + ROAD_WIDTH // 2


def on_road(x, y):
    return road_left(y) <= x <= road_right(y)


def on_shoulder(x, y):
    if on_road(x, y):
        return False
    return road_left(y) - SHOULDER_WIDTH <= x <= road_right(y) + SHOULDER_WIDTH


def lane_to_x(lane, y):
    return road_left(y) + lane * ROAD_WIDTH


def dist_at(y):
    return distance_traveled + (PLAYER_ROW - y)


def row_at(dist):
    return PLAYER_ROW - (dist - distance_traveled)


def new_race():
    global player_speed, distance_traveled, rival, game_state
    player_speed = 0.0
    distance_traveled = 0.0
    game_state = "racing"
    player.pos = (lane_to_x(0.75, PLAYER_ROW), PLAYER_ROW)
    rival = {
        "actor": Actor(random.choice(RIVAL_COLORS)),
        "distance": 0,
        "lane": 0.25,
        "base_speed": 6.5,
    }


new_race()


def draw():
    screen.fill(GRASS)

    strip_height = 10
    for top in range(0, HEIGHT, strip_height):
        y = top + strip_height // 2
        center_x = road_center_x(y)
        screen.draw.filled_rect(
            Rect(center_x - ROAD_WIDTH // 2 - SHOULDER_WIDTH, top,
                 SHOULDER_WIDTH, strip_height),
            GRAVEL,
        )
        screen.draw.filled_rect(
            Rect(center_x + ROAD_WIDTH // 2, top, SHOULDER_WIDTH, strip_height),
            GRAVEL,
        )
        screen.draw.filled_rect(
            Rect(center_x - ROAD_WIDTH // 2, top, ROAD_WIDTH, strip_height),
            TARMAC,
        )

        if dist_at(y) % DASH_PERIOD < DASH_LENGTH:
            screen.draw.filled_rect(Rect(center_x - 4, top, 8, strip_height), LINE)

    # >>>>>>>>>>>>>>>>>>>>>>
    # NEW (not in Week 2): draw the checkered finish line when it is on screen
    finish_y = row_at(FINISH_DISTANCE)
    if -20 < finish_y < HEIGHT:
        left = road_left(finish_y)
        for i in range(0, ROAD_WIDTH, 20):
            if (i // 20) % 2 == 0:
                color = "white"
            else:
                color = "black"
            screen.draw.filled_rect(Rect(left + i, finish_y - 8, 20, 16), color)
    # <<<<<<<<<<<<<<<<<<<<<<

    rival["actor"].draw()
    player.draw()

    screen.draw.text(f"Speed: {player_speed:0.1f}", topleft=(10, 10),
                     fontsize=30, color="white")
    # >>>>>>>>>>>>>>>>>>>>>>
    # CHANGED from Week 2: distance now shows "/ 3900" so you know how far to go
    screen.draw.text(f"Distance: {int(distance_traveled)} / {FINISH_DISTANCE} m", topleft=(10, 40),
                     fontsize=30, color="white")
    # <<<<<<<<<<<<<<<<<<<<<<

    if game_state == "crashed":
        _banner("CRASHED!", "Press SPACE to try again")
    # >>>>>>>>>>>>>>>>>>>>>>
    # NEW (not in Week 2): win and lose banners
    elif game_state == "won":
        _banner("YOU WIN!", "Press SPACE to race again")
    elif game_state == "lost":
        _banner("YOU LOSE!", "Press SPACE to race again")
    # <<<<<<<<<<<<<<<<<<<<<<


def _banner(title, subtitle):
    screen.draw.filled_rect(Rect(0, HEIGHT // 2 - 60, WIDTH, 120), (0, 0, 0))
    screen.draw.text(title, center=(WIDTH // 2, HEIGHT // 2 - 15),
                     fontsize=60, color="white")
    screen.draw.text(subtitle, center=(WIDTH // 2, HEIGHT // 2 + 30),
                     fontsize=30, color="white")


def update():
    global player_speed, distance_traveled, game_state

    if game_state != "racing":
        if keyboard.space:
            new_race()
        return

    if keyboard.left:
        player.x -= 5
    if keyboard.right:
        player.x += 5
    player.x = max(20, min(WIDTH - 20, player.x))

    if keyboard.up:
        player_speed += ACCEL
    elif keyboard.down:
        player_speed -= BRAKE
    else:
        player_speed -= COAST

    if on_shoulder(player.x, PLAYER_ROW):
        if player_speed > SHOULDER_MAX_SPEED:
            player_speed -= ROUGH_BRAKE
    elif not on_road(player.x, PLAYER_ROW):
        if player_speed > ROUGH_MAX_SPEED:
            player_speed -= ROUGH_BRAKE
    player_speed = max(0.0, min(MAX_SPEED, player_speed))

    distance_traveled += player_speed

    rival["distance"] += rival["base_speed"]
    rival_y = row_at(rival["distance"])
    rival["actor"].pos = (lane_to_x(rival["lane"], rival_y), rival_y)

    if player.colliderect(rival["actor"]):
        game_state = "crashed"
    # >>>>>>>>>>>>>>>>>>>>>>
    # NEW (not in Week 2): first car to the finish line wins
    elif distance_traveled >= FINISH_DISTANCE:
        game_state = "won"
    elif rival["distance"] >= FINISH_DISTANCE:
        game_state = "lost"
    # <<<<<<<<<<<<<<<<<<<<<<
