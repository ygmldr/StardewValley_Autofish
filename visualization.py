import pygame
import random
from fish_simulator import FishSimulator
import itertools
import torch
from DQN import DQN

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Game settings
BAR_WIDTH = 50
BAR_HEIGHT = 200
FISH_SIZE = 10
PROGRESS_BAR_WIDTH = 20
PROGRESS_BAR_HEIGHT = 300


def runGame(level=16, motion_type=0, difficulty=70):
    # Initialize Pygame
    pygame.init()
    simulator = FishSimulator()
    simulator.reset(level, motion_type, difficulty)
    # Initialize screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Fishing Game")

    # Game variables
    catching = False

    # Main game loop
    running = True
    clock = pygame.time.Clock()
    t = 0
    distance_from_catching = 0

    preparing = False
    perfect = True

    while running:
        t += 1
        bobber_bar_height, bobber_position, bobber_bar_pos, distance_from_catching = (
            simulator.get_draw_state())

        print(
            f"t:{t}, bobber_bar_height: {bobber_bar_height}, bobber_position: {bobber_position}, bobber_bar_pos: {bobber_bar_pos}, distance_from_catching: {distance_from_catching}")

        fish_pos = [SCREEN_WIDTH // 2, int(bobber_position) / 568 * SCREEN_HEIGHT]
        bar_pos = [SCREEN_WIDTH // 2 - BAR_WIDTH // 2, bobber_bar_pos / 548 * SCREEN_HEIGHT]

        # Clear screen
        screen.fill(WHITE)

        # Draw vertical bar
        pygame.draw.rect(screen, BLUE, (*bar_pos, BAR_WIDTH, bobber_bar_height))

        # Draw fish
        pygame.draw.circle(screen, GREEN, fish_pos, FISH_SIZE)

        # Draw progress bar
        pygame.draw.rect(screen, BLACK, (
            SCREEN_WIDTH - 50, SCREEN_HEIGHT // 2 - PROGRESS_BAR_HEIGHT // 2, PROGRESS_BAR_WIDTH, PROGRESS_BAR_HEIGHT))
        pygame.draw.rect(screen, RED, (
            SCREEN_WIDTH - 50,
            SCREEN_HEIGHT // 2 - PROGRESS_BAR_HEIGHT // 2 + (1 - distance_from_catching) * PROGRESS_BAR_HEIGHT,
            PROGRESS_BAR_WIDTH, distance_from_catching * PROGRESS_BAR_HEIGHT))

        # Update display
        pygame.display.flip()

        while preparing:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    preparing = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    preparing = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                catching = True
            elif event.type == pygame.MOUSEBUTTONUP:
                catching = False

        if catching:
            state, _, done, _ = simulator.update(True)
        else:
            state, _, done, _ = simulator.update(False)

        perfect = state[6]
        # Cap the frame rate
        clock.tick(60)
        if done:
            break

    if distance_from_catching >= 0.9:
        print(f"You caught the fish!, perfect:{perfect}")
    else:
        print("The fish got away!")
    pygame.quit()


def select_action(model, state):
    with torch.no_grad():
        # t.max(1) will return the largest column value of each row.
        # second column on max result is index of where max element was
        # found, so we pick action with the larger expected reward.
        state = torch.tensor(state, dtype=torch.float32, device=device).unsqueeze(0)

        return model(state).max(1).indices.view(1, 1)


def runGameWithModel(model_path):
    # Initialize Pygame
    pygame.init()
    simulator = FishSimulator()
    state = simulator.resetRandomly()
    print(f'player level:{simulator.bobber_bar_height / 8 - 12}, fish type: {simulator.motion_type}, difficulty: {simulator.difficulty}')
    # Initialize screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Fishing Game")

    # Load the trained model
    policy_net = DQN(7, 2).to(device)
    policy_net.load_state_dict(torch.load(model_path, map_location=device))
    policy_net.eval()

    # Main game loop
    running = True
    clock = pygame.time.Clock()
    t = 0
    distance_from_catching = 0

    preparing = False
    perfect = True

    while running:
        t += 1
        bobber_bar_height, bobber_position, bobber_bar_pos, distance_from_catching = (
            simulator.get_draw_state())

        fish_pos = [SCREEN_WIDTH // 2, int(bobber_position) / 568 * SCREEN_HEIGHT]
        bar_pos = [SCREEN_WIDTH // 2 - BAR_WIDTH // 2, bobber_bar_pos / 548 * SCREEN_HEIGHT]

        # Clear screen
        screen.fill(WHITE)

        # Draw vertical bar
        pygame.draw.rect(screen, BLUE, (*bar_pos, BAR_WIDTH, bobber_bar_height))

        # Draw fish
        pygame.draw.circle(screen, GREEN, fish_pos, FISH_SIZE)

        # Draw progress bar
        pygame.draw.rect(screen, BLACK, (
            SCREEN_WIDTH - 50, SCREEN_HEIGHT // 2 - PROGRESS_BAR_HEIGHT // 2, PROGRESS_BAR_WIDTH, PROGRESS_BAR_HEIGHT))
        pygame.draw.rect(screen, RED, (
            SCREEN_WIDTH - 50,
            SCREEN_HEIGHT // 2 - PROGRESS_BAR_HEIGHT // 2 + (1 - distance_from_catching) * PROGRESS_BAR_HEIGHT,
            PROGRESS_BAR_WIDTH, distance_from_catching * PROGRESS_BAR_HEIGHT))

        # Update display
        pygame.display.flip()

        action = select_action(policy_net, state)

        if action:
            state, _, done, _ = simulator.update(True)
        else:
            state, _, done, _ = simulator.update(False)

        perfect = state[6]
        # Cap the frame rate
        clock.tick(60)
        if done:
            break

    if distance_from_catching >= 0.9:
        print(f"You caught the fish!, perfect:{perfect}")
    else:
        print("The fish got away!")
    pygame.quit()


if __name__ == '__main__':
    while True:
        runGameWithModel('policy_fishnet.pth')
        input()
