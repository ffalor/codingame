import sys
import math

# Deliver more amadeusium to hq (left side of the map) than your opponent. Use radars to find amadeusium but beware of traps!

# height: size of the map
width, height = [int(i) for i in input().split()]

NONE = -1
ROBOT_ALLY = 0
ROBOT_ENEMY = 1
HOLE = 1
RADAR = 2
TRAP = 3
AMADEUSIUM = 4


def debug_message(message):
    print(message, file=sys.stderr)


class Pos:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance(self, pos):
        return abs(self.x - pos.x) + abs(self.y - pos.y)


class Entity(Pos):
    def __init__(self, x, y, type, id):
        super().__init__(x, y)
        self.type = type
        self.id = id


class Robot(Entity):
    def __init__(self, x, y, type, id, item):
        super().__init__(x, y, type, id)
        self.item = item

    def is_dead(self):
        return self.x == -1 and self.y == -1

    @staticmethod
    def move(x, y, message=""):
        print(f"MOVE {x} {y} {message}")

    @staticmethod
    def wait(message=""):
        print(f"WAIT {message}")

    @staticmethod
    def dig(x, y, message=""):
        print(f"DIG {x} {y} {message}")

    @staticmethod
    def request(requested_item, message=""):
        if requested_item == RADAR:
            print(f"REQUEST RADAR {message}")
            game.radar_cooldown = 5
        elif requested_item == TRAP:
            print(f"REQUEST TRAP {message}")
            game.trap_cooldown = 5
        else:
            raise Exception(f"Unknown item {requested_item}")


class Cell(Pos):
    def __init__(self, x, y, amadeusium, hole):
        super().__init__(x, y)
        self.amadeusium = amadeusium
        self.hole = hole

    def has_hole(self):
        return self.hole == HOLE

    def update(self, amadeusium, hole):
        self.amadeusium = amadeusium
        self.hole = hole


class Grid:
    def __init__(self):
        self.cells = []
        for y in range(height):
            for x in range(width):
                self.cells.append(Cell(x, y, 0, 0))

    def get_cell(self, x, y):
        if width > x >= 0 and height > y >= 0:
            return self.cells[x + width * y]
        return None


class Game:
    def __init__(self):
        self.grid = Grid()
        self.my_score = 0
        self.enemy_score = 0
        self.radar_cooldown = 0
        self.trap_cooldown = 0
        self.radars = []
        self.traps = []
        self.my_robots = []
        self.enemy_robots = []

    def reset(self):
        self.radars = []
        self.traps = []
        self.my_robots = []
        self.enemy_robots = []


class TrapBot:
    def __init__(self):
        self.tiles_to_trap = [n for n in range(15)]

    def get_next_tile(self, robot: Robot):
        trapped = [t.y for t in game.traps]
        to_trap = [v for v in self.tiles_to_trap if v not in trapped]

        if self.get_trap():
            closest = to_trap[0]
            for y in to_trap:
                if (robot.distance(Pos(1, y)) < (robot.distance(Pos(1, closest)))):
                    closest = y
            return 1, closest

    def get_trap(self):
        trapped = [t.y for t in game.traps]
        to_trap = [c for c in self.tiles_to_trap if c not in trapped]
        if to_trap:
            return True
        return False


class FarmBot:
    def __init__(self):
        self.tiles_to_farm = []

    def update(self):
        self.tiles_to_farm = [
            t for t in game.grid.cells if t.amadeusium != "?" and int(t.amadeusium) > 0]

    def tile_to_farm(self, robot: Robot):
        to_farm = self.tiles_to_farm
        closest = to_farm[0]

        for tile in to_farm:
            if (robot.distance(Pos(tile.x, tile.y))) < (robot.distance(Pos(closest.x, closest.y))):
                closest = tile
        return closest.x, closest.y


class RadarBot:
    def __init__(self):
        self.tiles_to_radar = [[7, 8], [15, 8], [22, 8]]

    def get_next_tile(self, robot: Robot):
        radared = [[r.x, r.y] for r in game.radars]
        to_radar = [c for c in self.tiles_to_radar if c not in radared]

        if self.get_radar():
            closest = to_radar[0]
            for c in to_radar:
                if (robot.distance(Pos(*c)) < (robot.distance(Pos(*closest)))):
                    closest = c
            return closest[0], closest[1]

    def get_radar(self):
        radared = [[r.x, r.y] for r in game.radars]
        to_radar = [c for c in self.tiles_to_radar if c not in radared]
        if to_radar:
            return True
        return False


game = Game()
trapBot = TrapBot()
radarBot = RadarBot()
farmBot = FarmBot()

# game loop
while True:
    # my_score: Players score
    game.my_score, game.enemy_score = [int(i) for i in input().split()]
    for i in range(height):
        inputs = input().split()
        for j in range(width):
            # amadeusium: amount of amadeusium or "?" if unknown
            # hole: 1 if cell has a hole
            amadeusium = inputs[2 * j]
            hole = int(inputs[2 * j + 1])
            game.grid.get_cell(j, i).update(amadeusium, hole)
    # entity_count: number of entities visible to you
    # radar_cooldown: turns left until a new radar can be requested
    # trap_cooldown: turns left until a new trap can be requested
    entity_count, game.radar_cooldown, game.trap_cooldown = [
        int(i) for i in input().split()]

    farmBot.update()
    game.reset()

    for i in range(entity_count):
        # id: unique id of the entity
        # type: 0 for your robot, 1 for other robot, 2 for radar, 3 for trap
        # y: position of the entity
        # item: if this entity is a robot, the item it is carrying (-1 for NONE, 2 for RADAR, 3 for TRAP, 4 for AMADEUSIUM)
        id, type, x, y, item = [int(j) for j in input().split()]

        if type == ROBOT_ALLY:
            game.my_robots.append(Robot(x, y, type, id, item))
        elif type == ROBOT_ENEMY:
            game.enemy_robots.append(Robot(x, y, type, id, item))
        elif type == TRAP:
            game.traps.append(Entity(x, y, type, id))
        elif type == RADAR:
            game.radars.append(Entity(x, y, type, id))


####################################################################################################
#                                           Main Loop                                              #
#                                           Main Loop                                              #
#                                           Main Loop                                              #
#                                           Main Loop                                              #
#                                           Main Loop                                              #
####################################################################################################
    for i in range(len(game.my_robots)):

        print("My Score   : ", game.my_score, file=sys.stderr)
        print("Enemy Score: ", game.enemy_score, file=sys.stderr)
        print("="*8, file=sys.stderr)

        robot = game.my_robots[i]

        if robot.is_dead():
            robot.wait(f"I'm dead... waiting {i}")
            continue

        if robot.item == AMADEUSIUM:
            robot.move(0, robot.y, "Return to HQ")
            continue

        if robot.item == NONE and game.trap_cooldown == 0 and trapBot.get_trap():
            robot.request(TRAP, "Requesting TRAP")
            continue

        if robot.item == NONE and game.radar_cooldown == 0 and radarBot.get_radar():
            robot.request(RADAR, "Requesting Radar")
            continue

        if farmBot.tiles_to_farm and robot.item == NONE:
            x, y = farmBot.tile_to_farm(robot)
            robot.dig(x, y, "Digging")
            continue

        if robot.item == TRAP:
            cords = trapBot.get_next_tile(robot)
            if cords:
                x, y = cords
                robot.dig(x, y, f"Placing trap on {x} {y}")
                continue

        if robot.item == RADAR:
            cords = radarBot.get_next_tile(robot)
            if cords:
                x, y = cords
                robot.dig(x, y, f"Placing radar on {x} {y}")
                continue
            robot.dig(robot.x, robot.y)
            continue

        robot.wait("waiting")
