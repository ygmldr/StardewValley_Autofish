"""
    Simulator of real stardew valley fishing
"""

import random


def equal(a, b, eps=1e-4):
    """
    :param a: number to compare
    :param b: number to compare
    :param eps: eps of the comparison
    :return:
        if |a - b| < eps, return True
    """
    return abs(a - b) < eps


class FishSimulator:
    """
        Simulator of real stardew valley fishing
    """

    def __init__(self):
        self.bobber_bar_height = None
        self.motion_type = None
        self.difficulty = None
        self.bobber_position = None
        self.bobber_bar_pos = None
        self.bobber_target_position = None
        self.floater_sinker_acceleration = None
        self.bobber_acceleration = None
        self.bobber_speed = None
        self.bobber_in_bar = None
        self.button_pressed = None
        self.bobber_bar_speed = None
        self.distance_from_catching = None
        self.perfect = None
        self.reset(level=10, motion_type=0, difficulty=100)

    def get_draw_state(self):
        """
        :return: states
        """
        return [self.bobber_bar_height, self.bobber_position, self.bobber_bar_pos,
                self.distance_from_catching]

    def resetRandomly(self):
        level = random.randint(7, 12)
        motion_type = random.randint(0, 4)
        difficulty = random.randint(40, 130)
        self.reset(level, motion_type, difficulty)
        return [self.bobber_bar_height, self.bobber_position, self.bobber_bar_pos,
                 self.bobber_in_bar, self.bobber_bar_speed, self.distance_from_catching, self.perfect]

    def reset(self, level=10, motion_type=0, difficulty=100):
        """
        :param level: fishing level
        :param motion_type: fish motion type
            mixed = 0, dart = 1, smooth = 2, sink = 3, floater = 4
        :param difficulty: fish difficulty
        """
        self.bobber_bar_height = 96 + level * 8
        self.motion_type = motion_type
        self.difficulty = difficulty
        self.bobber_position = 508
        self.bobber_bar_pos = 568 - self.bobber_bar_height
        self.bobber_target_position = (100.0 - self.difficulty) / 100.0 * 548.0
        self.floater_sinker_acceleration = 0
        self.bobber_acceleration = 0
        self.bobber_speed = 0
        self.bobber_in_bar = True
        self.button_pressed = False
        self.bobber_bar_speed = 0
        self.distance_from_catching = 0.1
        self.perfect = True

    def update(self, button_pressed):
        """
        :param button_pressed: action of player or AI
        :return:
            [states], Rewards, Done, Info
        """
        break_perfect = False
        if (random.random() < self.difficulty * (20 if self.motion_type == 2 else 1) / 4000 and
                self.motion_type != 2 or equal(self.bobber_target_position, -1)):
            num1 = 548 - self.bobber_position
            tmp_bobber_position = self.bobber_position
            num2 = min(99, self.difficulty + random.randint(10, 45)) / 100
            self.bobber_target_position = self.bobber_position + random.randint(int(min(-tmp_bobber_position, num1)), int(num1)) * num2

        if self.motion_type == 4:
            self.floater_sinker_acceleration = max(self.floater_sinker_acceleration - 0.01, -1.5)

        elif self.motion_type == 3:
            self.floater_sinker_acceleration = min(self.floater_sinker_acceleration + 0.01, 1.5)

        if abs(self.bobber_position - self.bobber_target_position) > 3 and self.bobber_target_position != -1:
            self.bobber_acceleration = (self.bobber_target_position - self.bobber_position) / (
                    random.randint(10, 30) + (100 - min(100, self.difficulty)))
            self.bobber_speed += (self.bobber_acceleration - self.bobber_speed) / 5
        else:
            if self.motion_type == 2 or random.random() >= self.difficulty / 2000:
                self.bobber_target_position = -1
            else:
                if random.random() < 0.5:
                    self.bobber_target_position = self.bobber_position + random.randint(-100, -51)
                else:
                    self.bobber_target_position = self.bobber_position + random.randint(50, 101)

        if self.motion_type == 1 and random.random() < self.difficulty / 1000.0:
            if random.random() < 0.5:
                self.bobber_target_position = (self.bobber_position +
                                               random.randint(-100 - int(self.difficulty) * 2, -51))
            else:
                self.bobber_target_position = (self.bobber_position +
                                               random.randint(50, 101 + int(self.difficulty) * 2))

        self.bobber_target_position = max(-1, min(548, self.bobber_target_position))
        self.bobber_position += self.bobber_speed + self.floater_sinker_acceleration
        self.bobber_position = min(532, self.bobber_position)
        self.bobber_position = max(0, self.bobber_position)

        self.bobber_in_bar = (self.bobber_position + 12.0 <= self.bobber_bar_pos - 32.0 + self.bobber_bar_height
                              and self.bobber_position - 16.0 >= self.bobber_bar_pos - 32.0)
        if self.bobber_position >= (548 - self.bobber_bar_height) and self.bobber_bar_pos >= (
                568 - self.bobber_bar_height - 4):
            self.bobber_in_bar = True

        self.button_pressed = button_pressed
        num4 = -0.25 if self.button_pressed else 0.25
        if self.button_pressed and num4 < 0.0 and (
                equal(self.bobber_bar_pos, 0) or equal(self.bobber_bar_pos, (568 - self.bobber_bar_height))):
            self.bobber_bar_speed = 0.0

        if self.bobber_in_bar:
            num4 *= 0.6

        self.bobber_bar_speed += num4
        self.bobber_bar_pos += self.bobber_bar_speed

        if self.bobber_bar_pos + self.bobber_bar_height > 568.0:  # 触底反弹
            self.bobber_bar_pos = 568 - self.bobber_bar_height
            self.bobber_bar_speed = -self.bobber_bar_speed * 2.0 / 3.0
        elif self.bobber_bar_pos < 0:
            self.bobber_bar_pos = 0
            self.bobber_bar_speed = -self.bobber_bar_speed * 2.0 / 3.0

        # update the progress bar

        if self.bobber_in_bar:
            self.distance_from_catching += 1 / 500
        else:
            self.distance_from_catching -= 3 / 1000
            if self.perfect:
                self.perfect = False
                break_perfect = True

        if self.distance_from_catching >= 1:
            reward = 50 + (200 if self.perfect else 0)

            return ([self.bobber_bar_height / 568, self.bobber_position / 568, self.bobber_bar_pos / 568,
                    self.bobber_in_bar, self.bobber_bar_speed, self.distance_from_catching, self.perfect],
                    reward, True, {})
        if self.distance_from_catching <= 0:
            reward = -50

            return ([self.bobber_bar_height, self.bobber_position, self.bobber_bar_pos,
                     self.bobber_in_bar, self.bobber_bar_speed, self.distance_from_catching, self.perfect],
                    reward, True, {})

        reward = 1 if self.bobber_in_bar else -1
        if break_perfect:
            reward -= 10
        if self.perfect:
            reward += 0.5

        return ([self.bobber_bar_height, self.bobber_position, self.bobber_bar_pos,
                 self.bobber_in_bar, self.bobber_bar_speed, self.distance_from_catching, self.perfect],
                reward, False, {})


if __name__ == '__main__':
    pass
