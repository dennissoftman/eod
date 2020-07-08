class vec2:
    x: float
    y: float

    def __init__(self, x=0., y=0.):
        self.x = x
        self.y = y

    def __sub__(self, other):
        return vec2(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return vec2(self.x + other.x, self.y + other.y)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def __mul__(self, other: float):
        return vec2(self.x*other, self.y*other)

    def __idiv__(self, other: float):
        if other != 0.:
            self.x /= other
            self.y /= other
        return self

    def __imul__(self, other: float):
        self.x *= other
        self.y *= other
        return self

    def __abs__(self):
        return vec2(abs(self.x), abs(self.y))

    def __round__(self, n=None):
        return vec2(round(self.x), round(self.y))

    def __len__(self):
        return (self.x * self.x + self.y * self.y)**0.5

    def __le__(self, other):
        if self.x <= other.x and self.y <= other.y:
            return True
        return False

    def normalized(self):
        if self.__len__() == 0:
            return vec2(0, 0)
        return vec2(self.x, self.y) * (1. / self.__len__())

    def in_rect(self, top_left, bot_right) -> bool:
        return (top_left.x <= self.x <= bot_right.x) and (top_left.y <= self.y <= bot_right.y)

    # helper function for pygame.draw
    def data(self) -> tuple:
        return round(self.x), round(self.y)


class icolor:
    r: int
    g: int
    b: int

    def __init__(self, val: tuple = (0, 0, 0)):
        self.r = val[0]
        self.g = val[1]
        self.b = val[2]

    def mix(self, other):
        self.r = (self.r + other.r) * 0.5
        self.g = (self.g + other.g) * 0.5
        self.b = (self.b + other.b) * 0.5

    def data(self) -> tuple:
        return self.r, self.g, self.b