"""
This is an minecraft-like voxel game.

WASD for move, TAB for toggle Fly.



"""
from __future__ import division
from modules.var import *
from modules.logs import *

import sys
import psutil
import platform
from datetime import datetime
import math
import random
import time

from collections import deque
from pyglet import image
from pyglet.gl import *
from pyglet.graphics import TextureGroup
from pyglet.window import key, mouse

JUMP_SPEED = math.sqrt(2 * GRAVITY * MAX_JUMP_HEIGHT)
TERMINAL_VELOCITY = 50

PLAYER_HEIGHT = 2
#Overworld
class Perlin:
    def __call__(self,x,y): return int(sum(self.noise(x*s,y*s)*h for s,h in self.perlins)*self.avg)
    def __init__(self):
        lissage = 32000
        lissage2 = lissage *2
        self.m = 131072; p = list(range(self.m)); random.shuffle(p); self.p = p+p
        p = self.perlins = tuple((1/i,i) for i in (32, 64) for j in range(2)) #,20,22,31,32,64,512, 1024
        self.avg = 16*len(p)/sum(f+i for f,i in p)

    def fade(self,t): return t*t*t*(t*(t*6-15)+10)
    def lerp(self,t,a,b): return a+t*(b-a)
    def grad(self,hash,x,y,z):
        h = hash&15; u = y if h&8 else x
        v = (x if h==12 or h==14 else z) if h&12 else y
        return (u if h&1 else -u)+(v if h&2 else -v)

    def noise(self,x,y,z=0):
        p,fade,lerp,grad = self.p,self.fade,self.lerp,self.grad
        xf,yf,zf = math.floor(x),math.floor(y),math.floor(z)
        X,Y,Z = xf%self.m,yf%self.m,zf%self.m
        x-=xf; y-=yf; z-=zf
        u,v,w = fade(x),fade(y),fade(z)
        A = p[X  ]+Y; AA = p[A]+Z; AB = p[A+1]+Z
        B = p[X+1]+Y; BA = p[B]+Z; BB = p[B+1]+Z
        return lerp(w,lerp(v,lerp(u,grad(p[AA],x,y,z),grad(p[BA],x-1,y,z)),lerp(u,grad(p[AB],x,y-1,z),grad(p[BB],x-1,y-1,z))),
                      lerp(v,lerp(u,grad(p[AA+1],x,y,z-1),grad(p[BA+1],x-1,y,z-1)),lerp(u,grad(p[AB+1],x,y-1,z-1),grad(p[BB+1],x-1,y-1,z-1))))
#Nether
class PerlinNether:
    def __call__(self,x,y): return int(sum(self.noise(x*s,y*s)*h for s,h in self.perlins)*self.avg)
    def __init__(self):
        self.m = 131072; p = list(range(self.m)); random.shuffle(p); self.p = p+p
        p = self.perlins = tuple((1/i,i) for i in (32, 64) for j in range(2)) #,20,22,31,32,64,512, 1024
        
        self.avg = 16*len(p)/sum(f+i for f,i in p)

    def fade(self,t): return t*t*t*(t*(t*6-15)+10)
    def lerp(self,t,a,b): return a+t*(b-a)
    def grad(self,hash,x,y,z):
        h = hash&15; u = y if h&8 else x
        v = (x if h==12 or h==14 else z) if h&12 else y
        return (u if h&1 else -u)+(v if h&2 else -v)

    def noise(self,x,y,z=0):
        p,fade,lerp,grad = self.p,self.fade,self.lerp,self.grad
        xf,yf,zf = math.floor(x),math.floor(y),math.floor(z)
        X,Y,Z = xf%self.m,yf%self.m,zf%self.m
        x-=xf; y-=yf; z-=zf
        u,v,w = fade(x),fade(y),fade(z)
        A = p[X  ]+Y; AA = p[A]+Z; AB = p[A+1]+Z
        B = p[X+1]+Y; BA = p[B]+Z; BB = p[B+1]+Z
        return lerp(w,lerp(v,lerp(u,grad(p[AA],x,y,z),grad(p[BA],x-1,y,z)),lerp(u,grad(p[AB],x,y-1,z),grad(p[BB],x-1,y-1,z))),
                      lerp(v,lerp(u,grad(p[AA+1],x,y,z-1),grad(p[BA+1],x-1,y,z-1)),lerp(u,grad(p[AB+1],x,y-1,z-1),grad(p[BB+1],x-1,y-1,z-1))))
class PerlinCave:
    def __call__(self,x,y): return int(sum(self.noise(x*s,y*s)*h for s,h in self.perlins)*self.avg)
    def __init__(self):
        self.m = 131072; p = list(range(self.m)); random.shuffle(p); self.p = p+p
        p = self.perlins = tuple((1/i,i) for i in (16, 32) for j in range(2)) #,20,22,31,32,64,512, 1024
        
        self.avg = 16*len(p)/sum(f+i for f,i in p)

    def fade(self,t): return t*t*t*(t*(t*6-15)+10)
    def lerp(self,t,a,b): return a+t*(b-a)
    def grad(self,hash,x,y,z):
        h = hash&15; u = y if h&8 else x
        v = (x if h==12 or h==14 else z) if h&12 else y
        return (u if h&1 else -u)+(v if h&2 else -v)

    def noise(self,x,y,z=0):
        p,fade,lerp,grad = self.p,self.fade,self.lerp,self.grad
        xf,yf,zf = math.floor(x),math.floor(y),math.floor(z)
        X,Y,Z = xf%self.m,yf%self.m,zf%self.m
        x-=xf; y-=yf; z-=zf
        u,v,w = fade(x),fade(y),fade(z)
        A = p[X  ]+Y; AA = p[A]+Z; AB = p[A+1]+Z
        B = p[X+1]+Y; BA = p[B]+Z; BB = p[B+1]+Z
        return lerp(w,lerp(v,lerp(u,grad(p[AA],x,y,z),grad(p[BA],x-1,y,z)),lerp(u,grad(p[AB],x,y-1,z),grad(p[BB],x-1,y-1,z))),
                      lerp(v,lerp(u,grad(p[AA+1],x,y,z-1),grad(p[BA+1],x-1,y,z-1)),lerp(u,grad(p[AB+1],x,y-1,z-1),grad(p[BB+1],x-1,y-1,z-1))))


def invertNumbers(nb):
    nb2 = nb*2
    nb3 = nb - nb2
    return nb3

if sys.version_info[0] >= 3:
    xrange = range

def cube_vertices(x, y, z, n):
    """ Return the vertices of the cube at position x, y, z with size 2*n.

    """
    return [
        x-n,y+n,z-n, x-n,y+n,z+n, x+n,y+n,z+n, x+n,y+n,z-n,  # top
        x-n,y-n,z-n, x+n,y-n,z-n, x+n,y-n,z+n, x-n,y-n,z+n,  # bottom
        x-n,y-n,z-n, x-n,y-n,z+n, x-n,y+n,z+n, x-n,y+n,z-n,  # left
        x+n,y-n,z+n, x+n,y-n,z-n, x+n,y+n,z-n, x+n,y+n,z+n,  # right
        x-n,y-n,z+n, x+n,y-n,z+n, x+n,y+n,z+n, x-n,y+n,z+n,  # front
        x+n,y-n,z-n, x-n,y-n,z-n, x-n,y+n,z-n, x+n,y+n,z-n,  # back
    ]


def tex_coord(x, y, n=8):
    """ Return the bounding vertices of the texture square.

    """
    m = 1.0 / n
    dx = x * m
    dy = y * m
    return dx, dy, dx + m, dy, dx + m, dy + m, dx, dy + m


def tex_coords(top, bottom, side):
    """ Return a list of the texture squares for the top, bottom and side.

    """
    top = tex_coord(*top)
    bottom = tex_coord(*bottom)
    side = tex_coord(*side)
    result = []
    result.extend(top)
    result.extend(bottom)
    result.extend(side * 4)
    return result


TEXTURE_PATH = 'ressourcepacks/' + textures_image
#HAUT, BAS, COTE
GRASS = tex_coords((0, 1), (1, 0), (0, 0))
SAND = tex_coords((1, 1), (1, 1), (1, 1))
BRICK = tex_coords((2, 0), (2, 0), (2, 0))
BEDROCK = tex_coords((2, 1), (2, 1), (2, 1))
DIRT = tex_coords((1, 0), (1,0),(1,0))
WATER_SOURCE = tex_coords((0,2),(0,2),(0,2))
STONE = tex_coords((1,2),(1,2),(1,2))
GLOWSTONE = tex_coords((2,2),(2,2),(2,2))
IRON_ORE = tex_coords((0,3),(0,3),(0,3))
GOLD_ORE = tex_coords((1,3),(1,3),(1,3))
DIAMOND_ORE = tex_coords((2,3),(2,3),(2,3))
COAL_ORE = tex_coords((3,3),(3,3),(3,3))
OAK_LOG = tex_coords((3,0),(3,0),(3,2))
OAK_LEAVES = tex_coords((3,1),(3,1),(3,1))
NETHERRACK = tex_coords((5, 0),(5, 0),(5, 0))
LAVA_SOURCE = tex_coords((4, 0),(4, 0),(4, 0))
COBBLESTONE = tex_coords((4, 1),(4, 1),(4, 1))
OAK_PLANKS = tex_coords((6, 0),(6, 0),(6, 0))
MOSSY_STONE_BRICKS = tex_coords((4, 2),(4, 2),(4, 2))
STONE_BRICKS = tex_coords((4, 3),(4, 3),(4, 3))
OBSIDIAN = tex_coords((5, 1),(5, 1),(5, 1))
SNOW_BLOCK = tex_coords((0, 4),(0, 4),(0, 4))
SNOW_GRASS = tex_coords((0,4), (1,0), (1,4))
SPRUCE_LOG = tex_coords((3, 4), (3,4),(2,4))
SPRUCE_LEAVES = tex_coords((4,4),(4,4),(4,4))
MAGMA_BLOCK = tex_coords((4,3),(4,3),(4,3))


"""

Rarity :
Coal : 10% in the world gen
Iron : 2% in the world gen
Gold : 1% in the world gen
Diamond : 1% in the world gen







"""

FACES = [
    ( 0, 1, 0),
    ( 0,-1, 0),
    (-1, 0, 0),
    ( 1, 0, 0),
    ( 0, 0, 1),
    ( 0, 0,-1),
]


def normalize(position):
    """ Accepts `position` of arbitrary precision and returns the block
    containing that position.

    Parameters
    ----------
    position : tuple of len 3

    Returns
    -------
    block_position : tuple of ints of len 3

    """
    x, y, z = position
    x, y, z = (int(round(x)), int(round(y)), int(round(z)))
    return (x, y, z)


def sectorize(position):
    """ Returns a tuple representing the sector for the given `position`.

    Parameters
    ----------
    position : tuple of len 3

    Returns
    -------
    sector : tuple of len 3

    """
    x, y, z = normalize(position)
    x, y, z = x // SECTOR_SIZE, y // SECTOR_SIZE, z // SECTOR_SIZE
    return (x, 0, z)


class Model(object):

    def __init__(self):

        # A Batch is a collection of vertex lists for batched rendering.
        self.batch = pyglet.graphics.Batch()

        # A TextureGroup manages an OpenGL texture.
        self.group = TextureGroup(image.load(TEXTURE_PATH).get_texture())

        # A mapping from position to the texture of the block at that position.
        # This defines all the blocks that are currently in the world.
        self.world = {}

        # Same mapping as `world` but only contains blocks that are shown.
        self.shown = {}

        # Mapping from position to a pyglet `VertextList` for all shown blocks.
        self._shown = {}

        # Mapping from sector to a list of positions inside that sector.
        self.sectors = {}

        # Simple function queue implementation. The queue is populated with
        # _show_block() and _hide_block() calls
        self.queue = deque()
        world = 2
        """

        1 : Sh*t world generation
        2 : Perlin Noise minecraftlike generation
        3 : No water Perlin Generation
        """
        if world == 1 :
            self._initialize_1()
        elif world == 2 :
            self._initialize_2()
        elif world == 3 :
            self._initialize_3()
        elif world == 4 :
            self._initialize_4()
        elif world == 5 :
            self._initialize_5()
    def _initialize_1(self):
        logs.log(1, "World Generation : N00B")
        blocks = 0
        logs.log(2, "Initializing World... This may take a moment")
        n = 80  # 1/2 width and height of world
        s = 1  # step size
        y = 0  # initial y height
        gen1 = 0
        # Initial
        for x in xrange(-n, n + 1, s):
            for z in xrange(-n, n + 1, s):
                # create a layer BEDROCK an grass everywhere.
                self.add_block((x, y , z), WATER_SOURCE, immediate=False)
                self.add_block((x, y - 1, z), SAND, immediate=False)
                self.add_block((x, y - 2, z), STONE, immediate=False)
                self.add_block((x, y - 3, z), STONE, immediate=False)
                self.add_block((x, y - 4, z), STONE, immediate=False)
                self.add_block((x, y - 5, z), STONE, immediate=False)
                self.add_block((x, y - 6, z), STONE, immediate=False)
                self.add_block((x, y - 7, z), STONE, immediate=False)
                self.add_block((x, y - 8, z), STONE, immediate=False)
                self.add_block((x, y - 9, z), STONE, immediate=False)
                self.add_block((x, y - 10, z), BEDROCK, immediate=False)
                blocks = blocks + 1
                if x in (-n, n) or z in (-n, n):
                    # create outer walls.
                    for dy in xrange(-2, 3):
                        self.add_block((x, y + dy, z), BEDROCK, immediate=False)
        for x in xrange(-n, n + 1, s):
            for z in xrange(-n, n + 1, s):
                for hauteur in range(-9, -2):
                    gen1 = random.randint(1, 100)
                    if gen1 == 34 or gen1 == 35 or gen1 == 46 or gen1 == 88 or gen1 == 96 or gen1 == 20 or gen1 == 86 or gen1 == 2 :
                        self.add_block((x, hauteur, z), COAL_ORE, immediate=False)
                    elif gen1 == 22 or gen1 == 90 :
                        self.add_block((x, hauteur, z), IRON_ORE, immediate=False)
                    elif gen1 == 45 :
                        self.add_block((x, hauteur, z), GOLD_ORE, immediate=False)
                    elif gen1 == 75 :
                        self.add_block((x, hauteur, z), DIAMOND_ORE, immediate=False)
                
                
                
                blocks = blocks + 1
        # generate the hills randomly
        o = n - 10
        cplus = 20
        cmoins = 50
        nombredecollines = random.randint(cplus, cmoins)
        logs.log(1, "Hills : " + str(nombredecollines))
        for _ in xrange(nombredecollines):
            a = random.randint(-o, o)  # x position of the hill
            b = random.randint(-o, o)  # z position of the hill
            c = -2  # base of the hill
            
            s = random.randint(3, 20)  # 2 * s is the side length of the hill
            F = s - 1
            h = random.randint(5, 19)  # height of the hill
            d = 1  # how quickly to taper off the hills
            for y in xrange(c, c + h):
                if y <1 :
                    t = SAND
                    for x in xrange(a - s, a + s + 1):
                        for z in xrange(b - s, b + s + 1):
                            if (x - a) ** 2 + (z - b) ** 2 > (s + 1) ** 2:
                                blocks = blocks + 1
                                continue
                            if (x - 0) ** 2 + (z - 0) ** 2 < 5 ** 2:
                                blocks = blocks + 1
                                continue
                            self.add_block((x, y, z), t, immediate=False)
                    s -= d  #
                else :
                    t = GRASS
                    for x in xrange(a - s, a + s + 1):
                        for z in xrange(b - s, b + s + 1):
                            if (x - a) ** 2 + (z - b) ** 2 > (s + 1) ** 2:
                                blocks = blocks + 1
                                continue
                            if (x - 0) ** 2 + (z - 0) ** 2 < 5 ** 2:
                                blocks = blocks + 1
                                continue
                            self.add_block((x, y, z), t, immediate=False)
                    s -= d  # decrement side length so hills taper off
        logs.log(2, "Blocks :" + str(blocks))

        
    def createTree(self,x, y, z, biome):
        if biome == "oak":
            self.add_block((x, y, z), OAK_LOG, immediate=False)
            self.add_block((x, y+1, z), OAK_LOG, immediate=False)
            self.add_block((x, y+2, z), OAK_LOG, immediate=False)
            self.add_block((x, y+3, z), OAK_LOG, immediate=False)
            self.add_block((x, y+4, z), OAK_LOG, immediate=False)
            for a in range(x-2, x+3):
                for b in range(z-2, z+3):
                    self.add_block((a, y+5, b), OAK_LEAVES, immediate=False)
                    self.add_block((a, y+6, b), OAK_LEAVES, immediate=False)
            for a in range(x-1, x+2):
                for b in range(z-1, z+2):
                    self.add_block((a, y+7, b), OAK_LEAVES, immediate=False)
        elif biome == "bush":
            for a in range(x-1, x+2):
                for b in range(z-1, z+2):
                    self.add_block((a, y, b), OAK_LEAVES, immediate=False)
                    self.add_block((a, y+1, b), OAK_LEAVES, immediate=False)
        elif biome == "nether":
            self.add_block((x, y, z), FIRE_OAK_LOG, immediate=False)
            self.add_block((x, y+1, z), FIRE_OAK_LOG, immediate=False)
            self.add_block((x, y+2, z), FIRE_OAK_LOG, immediate=False)
            self.add_block((x, y+3, z), FIRE_OAK_LOG, immediate=False)
            self.add_block((x, y+4, z), FIRE_OAK_LOG, immediate=False)
            for a in range(x-2, x+3):
                for b in range(z-2, z+3):
                    self.add_block((a, y+5, b), FIRE_OAK_LEAVES, immediate=False)
                    self.add_block((a, y+6, b), FIRE_OAK_LEAVES, immediate=False)
            for a in range(x-1, x+2):
                for b in range(z-1, z+2):
                    self.add_block((a, y+7, b), FIRE_OAK_LEAVES, immediate=False)
        elif biome == "snow":
            for aaa in range(x-2, x+3):
                for bbb in range(z-2, z+3):
                    self.add_block((aaa, y+4, bbb), SPRUCE_LEAVES, immediate=False)
                    self.add_block((aaa, y+6, bbb), SPRUCE_LEAVES, immediate=False)
            self.add_block((x+1, y+5, z), SPRUCE_LEAVES, immediate=False)
            self.add_block((x, y+5, z+1), SPRUCE_LEAVES, immediate=False)
            self.add_block((x-1, y+5, z), SPRUCE_LEAVES, immediate=False)
            self.add_block((x, y+5, z-1), SPRUCE_LEAVES, immediate=False)
            
            self.add_block((x+1, y+7, z), SPRUCE_LEAVES, immediate=False)
            self.add_block((x, y+7, z+1), SPRUCE_LEAVES, immediate=False)
            self.add_block((x-1, y+7, z), SPRUCE_LEAVES, immediate=False)
            self.add_block((x, y+7, z-1), SPRUCE_LEAVES, immediate=False)
            self.add_block((x, y+8, z), SPRUCE_LEAVES, immediate=False)
            self.add_block((x, y+7, z), SPRUCE_LOG, immediate=False)

            self.add_block((x, y, z), SPRUCE_LOG, immediate=False)
            self.add_block((x, y+1, z), SPRUCE_LOG, immediate=False)
            self.add_block((x, y+2, z), SPRUCE_LOG, immediate=False)
            self.add_block((x, y+3, z), SPRUCE_LOG, immediate=False)
            self.add_block((x, y+4, z), SPRUCE_LOG, immediate=False)
            self.add_block((x, y+5, z), SPRUCE_LOG, immediate=False)
            self.add_block((x, y+6, z), SPRUCE_LOG, immediate=False)
            



    
    def _initialize_2(self):
        logs.log(1, "World Generation : Realistic World Generation")
        _mapmaker = 128
        mapmaker = _mapmaker // 2
        block = 0
        perlin = Perlin()
        perlin1 = PerlinNether()
        logs.log(1, "Generation : 1/4")
        for x in range(-mapmaker, mapmaker):
            for z in range(-mapmaker, mapmaker):
                self.add_block((x, -4, z), WATER_SOURCE, immediate=False)
                self.add_block((x, -5, z), SAND, immediate=False)
                self.add_block((x, -6, z), STONE, immediate=False)
                for count in range(-20, -6):
                    mi = random.randint(1, 100)
                    if count > -21 :
                        if mi == 15 or mi == 25 or mi == 35 or mi == 45 or mi == 55 :
                            self.add_block((x, count, z), COAL_ORE, immediate=False)
                        elif mi == 20 or mi == 80 :
                            self.add_block((x, count, z), IRON_ORE, immediate=False)
                        elif mi == 75 :
                            self.add_block((x, count, z), GOLD_ORE, immediate=False)
                        elif mi == 60 :
                            self.add_block((x, count, z), DIAMOND_ORE, immediate=False)
                        else :
                            self.add_block((x, count, z), STONE, immediate=False)
                self.add_block((x, -21, z), BEDROCK, immediate=False)
        logs.log(1, "Generation : 2/4")
        for x in range(-mapmaker, mapmaker):
            for z in range(-mapmaker, mapmaker):
                mk = random.randint(1, 200)
                y = perlin(x,z)
                mw = random.randint(1, 50)
                zw = random.randint(1, 3)
                if mw == 25 or mw == 30:
                    self.add_block((x, y-6, z), GLOWSTONE, immediate=False)
                elif mw == 1 :
                    self.add_block((x, y-6, z), COBBLESTONE, immediate = False)
                if y < -3 and y > -5 :
                    self.add_block((x, y, z), SAND, immediate=False)
                elif y < -3 :
                    self.add_block((x, y, z), STONE, immediate=False)
                    gen1 = random.randint(1, 100)
                    if gen1 == 34 or gen1 == 35 or gen1 == 46 or gen1 == 88 or gen1 == 96 or gen1 == 20 or gen1 == 86 or gen1 == 2 :
                        self.add_block((x, y, z), COAL_ORE, immediate=False)
                    elif gen1 == 22 or gen1 == 90 :
                        self.add_block((x, y, z), IRON_ORE, immediate=False)
                    elif gen1 == 45 :
                        self.add_block((x, y, z), GOLD_ORE, immediate=False)
                    elif gen1 == 75 :
                        self.add_block((x, y, z), DIAMOND_ORE, immediate=False)
                elif y == 20 :
                    if zw == 2 :
                        self.add_block((x, y, z), SNOW_GRASS, immediate=False)
                    else :
                        self.add_block((x, y, z), GRASS, immediate=False)
                elif y > 20 :
                    self.add_block((x, y, z), SNOW_GRASS, immediate=False)
                    if mk == 50 :
                        self.createTree(x, y+1, z, "snow")
                else :
                    self.add_block((x, y, z), GRASS, immediate=False)
                    if mk == 50 :
                        self.createTree(x, y+1, z, "oak")
                    elif mk == 100 :
                        self.createTree(x, y+1, z, "bush")
                self.add_block((x, y-1, z), DIRT, immediate=False)
                if y > -3 :
                    self.add_block((x, y-2, z), DIRT, immediate=False)
                if y > -2 :
                    self.add_block((x, y-3, z), DIRT, immediate=False)
                if y > -1 :
                    self.add_block((x, y-4, z), DIRT, immediate=False)
                self.add_block((x, y-5, z), STONE, immediate=False)
        logs.log(1, "Generation : 3/4")
        lava = -74
        magma = lava + 1
        underlava = lava -1
        for x in range(-mapmaker, mapmaker):
            for z in range(-mapmaker, mapmaker):
                self.add_block((x, lava, z), LAVA_SOURCE, immediate=False)
                self.add_block((x, underlava, z), MAGMA_BLOCK, immediate=False)
        logs.log(1, "Generation : 4/4")
        for x in range(-mapmaker, mapmaker):
            for z in range(-mapmaker, mapmaker):
                y = perlin1(x, z)
                y2 = invertNumbers(y)
                y3 = y - 70
                if y3 == magma  or y3 == lava:
                    self.add_block((x, y-70, z), MAGMA_BLOCK, immediate=False)
                else :
                    self.add_block((x, y-70, z), NETHERRACK, immediate=False)
                self.add_block((x, y2-70, z), NETHERRACK, immediate=False)
                self.add_block((x, y-69, z), NETHERRACK, immediate=False)
                self.add_block((x, y-68, z), NETHERRACK, immediate=False)
                self.add_block((x, y2-71, z), NETHERRACK, immediate=False)
        logs.log(1, "Generation : Done !")
    def _initialize_3(self):
        logs.log(1, "World Generation : No water world generation")
        _mapmaker = 64
        mapmaker = _mapmaker // 2
        nether = True
        perlin = Perlin()
        
        for x in range(-mapmaker, mapmaker):
            for z in range(-mapmaker, mapmaker):
                mk = random.randint(1, 200)
                y = perlin(x,z)
                mw = random.randint(1, 50)
                self.add_block((x, y, z), GRASS, immediate=False)
                self.add_block((x, y-1, z), DIRT, immediate=False)
                self.add_block((x, y-2, z), DIRT, immediate=False)
                self.add_block((x, y-3, z), DIRT, immediate=False)
                if mk == 50 :
                    self.createTree(x, y+1, z, "oak")
                elif mk == 100 :
                    self.createTree(x, y+1, z, "bush")
    def _initialize_4(self):
        logs.log(1, "World Generation : Nether")
        _mapmaker = 128
        mapmaker = _mapmaker // 2
        perlin = PerlinNether()
        for x in range(-mapamaker, mapmaker):
            for z in range(-mapamaker, mapmaker):
                y = perlin(x, z)
                y2 = invertNumbers(y)
                self.add_block((x, y, z), NETHERRACK, immediate=False)
                self.add_block((x, y2, z), NETHERRACK, immediate=False)
                self.add_block((x, -6, z), LAVA_SOURCE, immediate=False)
    def _initialize_5(self):
        logs.log(1, "World Generation : Nether + No water")
        _mapmaker = 256
        mapmaker = _mapmaker // 2
        perlin1 = PerlinNether()
        perlin2 = Perlin()
        for x in range(-mapmaker, mapmaker):
            for z in range(-mapmaker, mapmaker):
                y1 = perlin1(x, z)
                y = perlin2(x, z)
                y2 = invertNumbers(y1)
                self.add_block((x, y1, z), NETHERRACK, immediate=False)
                self.add_block((x, y1+1, z), NETHERRACK, immediate=False)
                self.add_block((x, y2, z), NETHERRACK, immediate=False)
                self.add_block((x, y2-1, z), NETHERRACK, immediate=False)
                self.add_block((x, -6, z), LAVA_SOURCE, immediate=False)
                mk = random.randint(1, 200)
                y = perlin2(x,z)
                self.add_block((x, y+50, z), GRASS, immediate=False)
                self.add_block((x, y+49, z), DIRT, immediate=False)
                self.add_block((x, y+48, z), DIRT, immediate=False)
                self.add_block((x, y+47, z), DIRT, immediate=False)
                if mk == 50 :
                    self.createTree(x, y+51, z, "oak")
                elif mk == 100 :
                    self.createTree(x, y+51, z, "bush")
    def _initialize_6(self):
        logs.log(1, "World Generation : Advanced Cave Generation")
        _mapmaker = 128
        mapmaker = _mapmaker // 2
        perlinCave = PerlinCave()
                
                
                    
                
                    
    def hit_test(self, position, vector, max_distance=4):
        """ Line of sight search from current position. If a block is
        intersected it is returned, along with the block previously in the line
        of sight. If no block is found, return None, None.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position to check visibility from.
        vector : tuple of len 3
            The line of sight vector.
        max_distance : int
            How many blocks away to search for a hit.

        """
        m = 8
        x, y, z = position
        dx, dy, dz = vector
        previous = None
        for _ in xrange(max_distance * m):
            key = normalize((x, y, z))
            if key != previous and key in self.world:
                return key, previous
            previous = key
            x, y, z = x + dx / m, y + dy / m, z + dz / m
        return None, None

    def exposed(self, position):
        """ Returns False is given `position` is surrounded on all 6 sides by
        blocks, True otherwise.

        """
        x, y, z = position
        for dx, dy, dz in FACES:
            if (x + dx, y + dy, z + dz) not in self.world:
                return True
        return False

    def add_block(self, position, texture, immediate=True):
        if position in self.world:
            self.remove_block(position, immediate)
        self.world[position] = texture
        self.sectors.setdefault(sectorize(position), []).append(position)
        if immediate:
            if self.exposed(position):
                self.show_block(position)
            self.check_neighbors(position)

    def remove_block(self, position, immediate=True):
        del self.world[position]
        self.sectors[sectorize(position)].remove(position)
        if immediate:
            if position in self.shown:
                self.hide_block(position)
            self.check_neighbors(position)

    def check_neighbors(self, position):
        x, y, z = position
        for dx, dy, dz in FACES:
            key = (x + dx, y + dy, z + dz)
            if key not in self.world:
                continue
            if self.exposed(key):
                if key not in self.shown:
                    self.show_block(key)
            else:
                if key in self.shown:
                    self.hide_block(key)

    def show_block(self, position, immediate=True):
        texture = self.world[position]
        self.shown[position] = texture
        if immediate:
            self._show_block(position, texture)
        else:
            self._enqueue(self._show_block, position, texture)

    def _show_block(self, position, texture):
        x, y, z = position
        vertex_data = cube_vertices(x, y, z, 0.5)
        texture_data = list(texture)
        # create vertex list
        # FIXME Maybe `add_indexed()` should be used instead
        self._shown[position] = self.batch.add(24, GL_QUADS, self.group,
            ('v3f/static', vertex_data),
            ('t2f/static', texture_data))

    def hide_block(self, position, immediate=True):
        self.shown.pop(position)
        if immediate:
            self._hide_block(position)
        else:
            self._enqueue(self._hide_block, position)

    def _hide_block(self, position):
        self._shown.pop(position).delete()

    def show_sector(self, sector):
        for position in self.sectors.get(sector, []):
            if position not in self.shown and self.exposed(position):
                self.show_block(position, False)

    def hide_sector(self, sector):

        for position in self.sectors.get(sector, []):
            if position in self.shown:
                self.hide_block(position, False)

    def change_sectors(self, before, after):
        before_set = set()
        after_set = set()
        pad = 4
        for dx in xrange(-pad, pad + 1):
            for dy in [0]:  # xrange(-pad, pad + 1):
                for dz in xrange(-pad, pad + 1):
                    if dx ** 2 + dy ** 2 + dz ** 2 > (pad + 1) ** 2:
                        continue
                    if before:
                        x, y, z = before
                        before_set.add((x + dx, y + dy, z + dz))
                    if after:
                        x, y, z = after
                        after_set.add((x + dx, y + dy, z + dz))
        show = after_set - before_set
        hide = before_set - after_set
        for sector in show:
            self.show_sector(sector)
        for sector in hide:
            self.hide_sector(sector)

    def _enqueue(self, func, *args):
        """ Add `func` to the internal queue.

        """
        self.queue.append((func, args))

    def _dequeue(self):
        """ Pop the top function from the internal queue and call it.

        """
        func, args = self.queue.popleft()
        func(*args)

    def process_queue(self):
        start = time.perf_counter()
        while self.queue and time.perf_counter() - start < 1.0 / TICKS_PER_SEC:
            self._dequeue()

    def process_entire_queue(self):
        """ Process the entire queue with no breaks.

        """
        while self.queue:
            self._dequeue()


class Window(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)

        # Whether or not the window exclusively captures the mouse.
        self.exclusive = False
        logs.log(1, "Setting self.exclusive = False")

        # When flying gravity has no effect and speed is increased.
        self.flying = False
        logs.log(1, "Setting self.flying = False")
        # right, and 0 otherwise.
        self.strafe = [0, 0]
        logs.log(1, "Setting self.strafe = [0, 0]")
        self.position = (0, 100, 0)
        logs.log(1, "Setting self.position = (0, 1, 0)")
        self.rotation = (0, 0)
        logs.log(1, "Setting self.rotation = (0, 0)")

        # Which sector the player is currently in.
        self.sector = None
        logs.log(1, "Setting self.sector = None")

        # The crosshairs at the center of the screen.
        self.reticle = None
        logs.log(1, "Setting self.reticle = None")

        # Velocity in the y (upward) direction.
        self.dy = 0
        logs.log(1, "Setting self.dy = 0")

        # A list of blocks the player can place. Hit num keys to cycle.
        self.inventory = [BRICK, GRASS, SAND, DIRT, OAK_LOG, OAK_LEAVES, OAK_PLANKS]

        # The current block the user can place. Hit num keys to cycle.
        self.block = self.inventory[0]
        logs.log(1, "Setting self.block = self.inventory[0]")

        # Convenience list of num keys.
        self.num_keys = [
            key._1, key._2, key._3, key._4, key._5,
            key._6, key._7, key._8, key._9, key._0]

        # Instance of the model that handles the world.
        self.model = Model()

        # The label that is displayed in the top left of the canvas.
        self.label = pyglet.text.Label('', font_name='Arial', font_size=18,
            x=10, y=self.height - 10, anchor_x='left', anchor_y='top',
            color=(0, 0, 0, 255))

        # This call schedules the `update()` method to be called
        # TICKS_PER_SEC. This is the main game event loop.
        pyglet.clock.schedule_interval(self.update, 1.0 / TICKS_PER_SEC)

    def set_exclusive_mouse(self, exclusive):
        """ If `exclusive` is True, the game will capture the mouse, if False
        the game will ignore the mouse.

        """
        super(Window, self).set_exclusive_mouse(exclusive)
        self.exclusive = exclusive

    def get_sight_vector(self):
        """ Returns the current line of sight vector indicating the direction
        the player is looking.

        """
        x, y = self.rotation
        # y ranges from -90 to 90, or -pi/2 to pi/2, so m ranges from 0 to 1 and
        # is 1 when looking ahead parallel to the ground and 0 when looking
        # straight up or down.
        m = math.cos(math.radians(y))
        # dy ranges from -1 to 1 and is -1 when looking straight down and 1 when
        # looking straight up.
        dy = math.sin(math.radians(y))
        dx = math.cos(math.radians(x - 90)) * m
        dz = math.sin(math.radians(x - 90)) * m
        return (dx, dy, dz)

    def get_motion_vector(self):
        """ Returns the current motion vector indicating the velocity of the
        player.

        Returns
        -------
        vector : tuple of len 3
            Tuple containing the velocity in x, y, and z respectively.

        """
        if any(self.strafe):
            x, y = self.rotation
            strafe = math.degrees(math.atan2(*self.strafe))
            y_angle = math.radians(y)
            x_angle = math.radians(x + strafe)
            if self.flying:
                m = math.cos(y_angle)
                dy = math.sin(y_angle)
                if self.strafe[1]:
                    # Moving left or right.
                    dy = 0.0
                    m = 1
                if self.strafe[0] > 0:
                    # Moving backwards.
                    dy *= -1
                # When you are flying up or down, you have less left and right
                # motion.
                dx = math.cos(x_angle) * m
                dz = math.sin(x_angle) * m
            else:
                dy = 0.0
                dx = math.cos(x_angle)
                dz = math.sin(x_angle)
        else:
            dy = 0.0
            dx = 0.0
            dz = 0.0
        return (dx, dy, dz)

    def update(self, dt):
        """ This method is scheduled to be called repeatedly by the pyglet
        clock.

        Parameters
        ----------
        dt : float
            The change in time since the last call.

        """
        self.model.process_queue()
        sector = sectorize(self.position)
        if sector != self.sector:
            self.model.change_sectors(self.sector, sector)
            if self.sector is None:
                self.model.process_entire_queue()
            self.sector = sector
        m = 8
        dt = min(dt, 0.2)
        for _ in xrange(m):
            self._update(dt / m)

    def _update(self, dt):

        # walking
        speed = FLYING_SPEED if self.flying else WALKING_SPEED
        d = dt * speed # distance covered this tick.
        dx, dy, dz = self.get_motion_vector()
        # New position in space, before accounting for gravity.
        dx, dy, dz = dx * d, dy * d, dz * d
        # gravity
        if not self.flying:
            # Update your vertical speed: if you are falling, speed up until you
            # hit terminal velocity; if you are jumping, slow down until you
            # start falling.
            self.dy -= dt * GRAVITY
            self.dy = max(self.dy, -TERMINAL_VELOCITY)
            dy += self.dy * dt
        # collisions
        x, y, z = self.position
        x, y, z = self.collide((x + dx, y + dy, z + dz), PLAYER_HEIGHT)
        self.position = (x, y, z)

    def collide(self, position, height):
        # How much overlap with a dimension of a surrounding block you need to
        # have to count as a collision. If 0, touching terrain at all counts as
        # a collision. If .49, you sink into the ground, as if walking through
        # tall grass. If >= .5, you'll fall through the ground.
        pad = 0.25
        p = list(position)
        np = normalize(position)
        for face in FACES:  # check all surrounding blocks
            for i in xrange(3):  # check each dimension independently
                if not face[i]:
                    continue
                # How much overlap you have with this dimension.
                d = (p[i] - np[i]) * face[i]
                if d < pad:
                    continue
                for dy in xrange(height):  # check each height
                    op = list(np)
                    op[1] -= dy
                    op[i] += face[i]
                    if tuple(op) not in self.model.world:
                        continue
                    p[i] -= (d - pad) * face[i]
                    if face == (0, -1, 0) or face == (0, 1, 0):
                        # You are colliding with the ground or ceiling, so stop
                        # falling / rising.
                        self.dy = 0
                    break
        return tuple(p)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.exclusive:
            vector = self.get_sight_vector()
            block, previous = self.model.hit_test(self.position, vector)
            if (button == mouse.RIGHT) or \
                    ((button == mouse.LEFT) and (modifiers & key.MOD_CTRL)):
                # ON OSX, control + left click = right click.
                if previous:
                    self.model.add_block(previous, self.block)
            elif button == pyglet.window.mouse.LEFT and block:
                texture = self.model.world[block]
                if texture != BEDROCK:
                    self.model.remove_block(block)
        else:
            self.set_exclusive_mouse(True)

    def on_mouse_motion(self, x, y, dx, dy):
        if self.exclusive:
            m = 0.15
            x, y = self.rotation
            x, y = x + dx * m, y + dy * m
            y = max(-90, min(90, y))
            self.rotation = (x, y)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.W:
            self.strafe[0] -= 1
        elif symbol == key.S:
            self.strafe[0] += 1
        elif symbol == key.A:
            self.strafe[1] -= 1
        elif symbol == key.D:
            self.strafe[1] += 1
        elif symbol == key.SPACE:
            if self.dy == 0:
                self.dy = JUMP_SPEED
        elif symbol == key.ESCAPE:
            self.set_exclusive_mouse(False)
        elif symbol == key.TAB:
            self.flying = not self.flying
        elif symbol in self.num_keys:
            index = (symbol - self.num_keys[0]) % len(self.inventory)
            self.block = self.inventory[index]

    def on_key_release(self, symbol, modifiers):
        if symbol == key.W:
            self.strafe[0] += 1
        elif symbol == key.S:
            self.strafe[0] -= 1
        elif symbol == key.A:
            self.strafe[1] += 1
        elif symbol == key.D:
            self.strafe[1] -= 1

    def on_resize(self, width, height):
        # label
        self.label.y = height - 10
        # reticle
        if self.reticle:
            self.reticle.delete()
        x, y = self.width // 2, self.height // 2
        n = 10
        self.reticle = pyglet.graphics.vertex_list(4,
            ('v2i', (x - n, y, x + n, y, x, y - n, x, y + n))
        )

    def set_2d(self):
        """ Configure OpenGL to draw in 2d.

        """
        width, height = self.get_size()
        glDisable(GL_DEPTH_TEST)
        viewport = self.get_viewport_size()
        glViewport(0, 0, max(1, viewport[0]), max(1, viewport[1]))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, max(1, width), 0, max(1, height), -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def set_3d(self):
        """ Configure OpenGL to draw in 3d.

        """
        width, height = self.get_size()
        glEnable(GL_DEPTH_TEST)
        viewport = self.get_viewport_size()
        glViewport(0, 0, max(1, viewport[0]), max(1, viewport[1]))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(65.0, width / float(height), 0.1, 60.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        x, y = self.rotation
        glRotatef(x, 0, 1, 0)
        glRotatef(-y, math.cos(math.radians(x)), 0, math.sin(math.radians(x)))
        x, y, z = self.position
        glTranslatef(-x, -y, -z)

    def on_draw(self):
        """ Called by pyglet to draw the canvas.

        """
        self.clear()
        self.set_3d()
        glColor3d(1, 1, 1)
        self.model.batch.draw()
        self.draw_focused_block()
        self.set_2d()
        self.draw_label()
        self.draw_reticle()

    def draw_focused_block(self):
        """ Draw black edges around the block that is currently under the
        crosshairs.

        """
        vector = self.get_sight_vector()
        block = self.model.hit_test(self.position, vector)[0]
        if block:
            x, y, z = block
            vertex_data = cube_vertices(x, y, z, 0.51)
            glColor3d(0, 0, 0)
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            pyglet.graphics.draw(24, GL_QUADS, ('v3f/static', vertex_data))
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    def draw_label(self):
        """ Draw the label in the top left of the screen.

        """
        x, y, z = self.position
        self.label.text = '%02d (%.2f, %.2f, %.2f) %d / %d' % (
            pyglet.clock.get_fps(), x, y, z,
            len(self.model._shown), len(self.model.world))
        self.label.draw()

    def draw_reticle(self):
        """ Draw the crosshairs in the center of the screen.

        """
        glColor3d(0, 0, 0)
        self.reticle.draw(GL_LINES)


def setup_fog():
    """ Configure the OpenGL fog properties.

    """
    # Enable fog. Fog "blends a fog color with each rasterized pixel fragment's
    # post-texturing color."
    glEnable(GL_FOG)
    # Set the fog color.
    glFogfv(GL_FOG_COLOR, (GLfloat * 4)(0.5, 0.69, 1.0, 1))
    # Say we have no preference between rendering speed and quality.
    glHint(GL_FOG_HINT, GL_DONT_CARE)
    # Specify the equation used to compute the blending factor.
    glFogi(GL_FOG_MODE, GL_LINEAR)
    # How close and far away fog starts and ends. The closer the start and end,
    # the denser the fog in the fog range.
    gl1 = 20.0
    gl2 = 60.0
    glFogf(GL_FOG_START, gl1)
    logs.log(1, "Setting FOG_START to " + str(gl1))
    glFogf(GL_FOG_END, gl2)
    
    logs.log(1, "Setting FOG_END to " + str(gl2))
    logs.log(1,"Game Started !")
    


def setup(FOG):
    """ Basic OpenGL configuration.

    """
    # Set the color of "clear", i.e. the sky, in rgba.
    glClearColor(0.5, 0.69, 1.0, 1)
    # Enable culling (not rendering) of back-facing facets -- facets that aren't
    # visible to you.
    glEnable(GL_CULL_FACE)    # Set the texture minification/magnification function to GL_NEAREST (nearest
    # in Manhattan distance) to the specified texture coordinates. GL_NEAREST
    # "is generally faster than GL_LINEAR, but it can produce textured images
    # with sharper edges because the transition between texture elements is not
    # as smooth."
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    if FOG == True :
        setup_fog()
        logs.log(2, "Fog Enabled !")
    else :
        logs.log(2, "Fog Disabled !")


def main(FOG, FULL):
    logs.log(2,"Launching Game !")
    logs.log(2,f"Using python {sys.version_info.major}.{sys.version_info.minor}")
    logs.log(2,"System Information")
    uname = platform.uname()
    logs.log(2,f"System: {uname.system}")
    logs.log(2,f"Node Name: {uname.node}")
    logs.log(2,f"Release: {uname.release}")
    logs.log(2,f"Version: {uname.version}")
    logs.log(2,f"Machine: {uname.machine}")
    logs.log(2,f"Processor: {uname.processor}")
    window = Window(width=800, height=600, caption='Minecraft', resizable=True)
    # Hide the mouse cursor and prevent the mouse from leaving the window.
    window.set_exclusive_mouse(True)
    icon = pyglet.image.load("default/icon.png")
    window.set_icon(icon)
    setup(FOG)
    window.set_fullscreen(fullscreen=FULL)
    
    pyglet.app.run()


if __name__ == '__main__':
    main(FOG, FULL)
    logs.log(1, "Game finished")
    logs.log(1, "Shutting Down.")
