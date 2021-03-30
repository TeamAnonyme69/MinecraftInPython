from logs import *

TICKS_PER_SEC = 60
logs.log(1, "Setting Max Framerate to " + str(TICKS_PER_SEC))
SECTOR_SIZE = 8
logs.log(1, "Setting Render Distance to " + str(SECTOR_SIZE))


WALKING_SPEED = 7
logs.log(1, "Setting walking speed to " + str(WALKING_SPEED))
FLYING_SPEED = 20
GRAVITY = 20.0
logs.log(1, "Setting gravity to " + str(GRAVITY))
MAX_JUMP_HEIGHT = 1.3

FOG = True
logs.log(1, "Setting Fog to " + str(FOG))
