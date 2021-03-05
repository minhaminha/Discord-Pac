#character creator
import numpy
from level import Extra

class Character:

    def __init__(self, charID, emoji, start, direction, state, corner = [1,1], counter = 0, cooldown = 0):
        self.id = charID
        self.display = emoji
        self.coord = start
        self.state = state
        self.direction = direction
        self.origin = start.copy()
        self.corner = corner
        self.counter = counter
        self.cooldown = cooldown
        self.prevspace = start.copy()

    def changeemoji(self, state):
        self.state = state
        if self.id == "pac":
            if state == "begin":
                self.display = Extra[0]
            elif state == "powerup":
                self.display = Extra[2]
            elif state == "dead":
                self.display = Extra[1]
        else:
            if state == "random" or state == "chase":
                self.display = Extra[self.id]
            elif state == "run":
                self.display = Extra[7]
            elif state == "dead":
                self.display = Extra[17]

