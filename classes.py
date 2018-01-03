# -*- coding: utf-8 -*-
"""
Created on Tue Jan  2 16:44:35 2018

@author: conor
"""
import pygame, math

# Define some colors
BLACK    = (   0,   0,   0)
#GRAY     = ( 125, 125, 125)
GRAY     = ( 255, 210, 125)
WHITE    = ( 255, 255, 255)
RED      = ( 255,   0,   0)
BLUE     = (   0,   0, 255)
PURPLE   = ( 255,   0, 255)
LPURP    = ( 127,   0, 127)
GREEN    = (   0, 255,   0)
ORANGE   = ( 255, 165,   0)
YELLOW   = ( 255, 255,   0)
YELANGE  = ( 255, 210,   0)
w = 203

screen_width = 1203
screen_height = 600

# helper functions

# returns the distance between player and target
def dist(player,target):
    center_player = [player.rect.x+player.width/2,
                     player.rect.y + player.width/2]
    center_target = [target.rect.x+target.width/2,
                     target.rect.y + target.width/2]
    diff_x = (center_player[0] - center_target[0])**2
    diff_y = (center_player[1] - center_target[1])**2
    return(int(round(math.sqrt(diff_x + diff_y))))

def z_dist(a,b):
    return((a[0]-b[0])**2 + (a[1]-b[1])**2)

def one_step_check_new(unit,theta,battle):
    def point_in_aoe(z,area):
        c = [area.rect.x+area.radius,area.rect.y+area.radius]
        if(z_dist(z,c)<area.radius):
            return(True)
    zu = [unit.rect.x+unit.width/2, unit.rect.y+unit.width/2]
    for area in battle.aoe_list:
        dst = [zu[0]+2*math.cos(theta), zu[1]+2*math.sin(theta)]
        if point_in_aoe(dst,area):
            return(False,area)
    return(True,None)

def above_ray(unit,area,boss):
    m = (float(area.rect.y) - boss.rect.y)/(area.rect.x - boss.rect.x)
    return(unit.rect.y > m*unit.rect.x)

def missile_spawn(player,target,damage,battle):
    bullet = Bullet(damage,target,7)
    bullet.rect.x = player.rect.x
    bullet.rect.y = player.rect.y
    battle.all_sprites_list.add(bullet)
    battle.bullet_list.add(bullet)

def min_target(battle):
    min_hp = 1
    min_unit = battle.player
    for unit in battle.team_list:
        if(float(unit.health)/unit.max_health < min_hp):
            min_hp = float(unit.health)/unit.max_health
            min_unit = unit
    return(min_unit)

def f_theta(source,target):
    diff_y = float(target.rect.y - source.rect.y)
    diff_x = float(target.rect.x - source.rect.y)
    return(math.atan2(diff_y,diff_x))

def list_kill(unit,battle):
    if(unit.name == "Tank"):
        battle.tank_list.remove(unit)
    elif((unit.name == "Healer") or (unit.name == 'CHealer')):
        battle.healer_list.remove(unit)
    elif(unit.name == "Caster"):
        battle.caster_list.remove(unit)
    elif(unit.name == "Melee"):
        battle.melee_list.remove(unit)

# Scale stat at level s / smax to fit in size
def scale(s,smax,size):
    return((int(round(float(s)*size/smax))))

class Bullet(pygame.sprite.Sprite):
    """ This class represents the bullet (ranged attack). """
    def __init__(self,damage,target,vel):
        # Call the parent class (Sprite) constructor
        super(Bullet, self).__init__()
        self.image = pygame.Surface([15,15])
        self.image.fill(WHITE)
        self.image.set_colorkey(WHITE)
        pygame.draw.ellipse(self.image,GREEN,[0,0,15,15])
        self.rect = self.image.get_rect()
        self.vel = vel

        self.damage = damage
        self.target = target
        
    def update(self,battle=None):
        """ Move the bullet. """
        # Define angle theta between bullet and enemy
        tc = [self.target.rect.x + self.target.width/2,
              self.target.rect.y + self.target.width/2]
        sc = [self.rect.x + 7.5,self.rect.y+7.5]        
        diff_y = float(tc[1] - sc[1])
        diff_x = float(tc[0] - sc[0])
        theta = math.atan2(diff_y,diff_x)
        self.rect.y = int(round(self.rect.y + self.vel*math.sin(theta)))
        self.rect.x = int(round(self.rect.x + self.vel*math.cos(theta)))

class Player(pygame.sprite.Sprite):
    """ This class represents the Player. (tank) """
    max_health = 200
    health = 200
    name = "Tank"
    is_alive = True
    armor = 0.3
    width = 20
    shield_wall_ready = True
    def __init__(self):
        """ Set up the player on creation. """
        # Call the parent class (Sprite) constructor
        super(Player, self).__init__()
        self.image = pygame.Surface([20,20])
        self.image.fill(WHITE)
        self.image.set_colorkey(WHITE)
        pygame.draw.ellipse(self.image,BLACK,[0,0,20,20])
        self.rect = self.image.get_rect()
        
        self.change_x = 0
        self.change_y = 0
        
    def changespeed(self,x,y):
        self.change_x += x
        self.change_y += y
    
    
    def update(self,battle=None):
        """ Update the player's position and bars, keep inside screen """
        self.rect.x = self.rect.x + self.change_x
        if(self.rect.x > screen_width-20):
            self.rect.x = screen_width-20
        elif(self.rect.x < w):
            self.rect.x = w
        self.rect.y = self.rect.y + self.change_y
        if(self.rect.y > screen_height-20):
            self.rect.y = screen_height-20
        elif(self.rect.y < 0):
            self.rect.y = 0
    
    def shield_wall(self,battle):
        if self.shield_wall_ready:
            print(self.armor)
            self.armor *= 2
            self.shield_wall_ready = False
            pygame.time.set_timer(battle.shield_wall_on,10000)
            pygame.time.set_timer(battle.shield_wall_cd,30000)

class Melee(pygame.sprite.Sprite):
    health = 100
    max_health = 100
    mana = 1000
    name = "Melee"
    is_alive = True
    armor = 0.1
    width = 20
    damage_dealt = 0
    def __init__(self,target):
        super(Melee, self).__init__()
        self.image = pygame.Surface([20,20])
        self.image.fill(WHITE)
        self.image.set_colorkey(WHITE)
        pygame.draw.ellipse(self.image,GREEN,[0,0,20,20])
        self.rect = self.image.get_rect()
        self.target = target
        self.speed = 3
        #self.dst = [target.rect.x+target.radius,target.rect.y+target.radius]
    def in_aoe(self,battle):
        return(pygame.sprite.spritecollide(self,
                                       battle.aoe_list,
                                       False,
                                       pygame.sprite.collide_circle))
    def update(self,battle):
        #print("melee target = %s" % self.target.name)
        # If out of range, get closer
        if(len(self.in_aoe(battle))>0):
            a = self.in_aoe(battle)[0]
            sc = [self.rect.x+10,self.rect.y+10]
            sa = [a.rect.x+a.width/2,a.rect.y+a.width/2]
            diff_y = float(sc[1]-sa[1])
            diff_x = float(sc[0]-sa[0])
            theta = math.atan2(diff_y,diff_x)
            self.rect.y = int(round(self.rect.y + self.speed*math.sin(theta)))
            self.rect.x = int(round(self.rect.x + self.speed*math.cos(theta)))

        elif(dist(self,self.target)>30):
            diff_y = float(self.target.rect.y - self.rect.y)
            diff_x = float(self.target.rect.x - self.rect.x)
            theta = math.atan2(diff_y,diff_x)
            #if(one_step_check(self,theta) == True):
                #self.rect.y = int(round(self.rect.y + self.speed*math.sin(theta)))
                #self.rect.x = int(round(self.rect.x + self.speed*math.cos(theta)))
            boolean,area = one_step_check_new(self,theta,battle)
            if(boolean):
                self.rect.y = int(round(self.rect.y + self.speed*math.sin(theta)))
                self.rect.x = int(round(self.rect.x + self.speed*math.cos(theta)))
            else:
                print('Alt step')
                if(above_ray(self,area,self.target)):
                    self.rect.y = int(round(self.rect.y + 1))
                else:
                    self.rect.y = int(round(self.rect.y - 1))
        # If in range and have mana, cast
        else:
            if(self.mana >= 180 and self.target.frozen == False):
                self.mana -= 180
                missile_spawn(self,self.target,4,battle)
                self.damage_dealt += 10
        # Mana regen
        self.mana = min(1000,self.mana+3)

class Caster(pygame.sprite.Sprite):
    health = 100
    max_health = 100
    mana = 1000
    name = "Caster"
    is_alive = True
    armor = 0.1
    width = 20
    damage_dealt = 0
    def __init__(self,target):
        super(Caster, self).__init__()
        self.image = pygame.Surface([20,20])
        self.image.fill(WHITE)
        self.image.set_colorkey(WHITE)
        pygame.draw.ellipse(self.image,BLUE,[0,0,20,20])
        self.rect = self.image.get_rect()
        self.target = target
        self.mana_cost = 300
        self.damage = 5
    def in_aoe(self,battle):
        return(pygame.sprite.spritecollide(self,
                                       battle.aoe_list,
                                       False,
                                       pygame.sprite.collide_circle))
    def update(self,battle):
        # If in any AoE's, gtfo
        if(len(self.in_aoe(battle))>0):
            a = self.in_aoe(battle)[0]
            sc = [self.rect.x+10,self.rect.y+10]
            sa = [a.rect.x+a.width/2,a.rect.y+a.width/2]
            diff_y = float(sc[1]-sa[1])
            diff_x = float(sc[0]-sa[0])
            theta = math.atan2(diff_y,diff_x)
            self.rect.y = int(round(self.rect.y + 2*math.sin(theta)))
            self.rect.x = int(round(self.rect.x + 2*math.cos(theta)))
        # If out of range of target, get closer
        elif(dist(self,self.target)>150):
            diff_y = float(self.target.rect.y - self.rect.y)
            diff_x = float(self.target.rect.x - self.rect.x)
            theta = math.atan2(diff_y,diff_x)
            self.rect.y = int(round(self.rect.y + 2*math.sin(theta)))
            self.rect.x = int(round(self.rect.x + 2*math.cos(theta)))
        # If in range and have mana, cast
        else:
            if(self.mana >= self.mana_cost and self.target.frozen == False):
                self.mana -= self.mana_cost
                self.damage_dealt += self.damage
                missile_spawn(self,self.target,self.damage,battle)
        # Mana regen
        self.mana = min(1000,self.mana+3)

class Healer(pygame.sprite.Sprite):
    health = 100
    max_health = 100
    mana = 1000
    max_mana = 1000
    name = "Healer"
    range = 125
    is_alive = True
    armor = 0.1
    innervate_ready = True
    innervate_bool = False
    width = 20
    def __init__(self,target,mh):
        super(Healer, self).__init__()
        self.image = pygame.Surface([20,20])
        self.image.fill(WHITE)
        self.image.set_colorkey(WHITE)
        pygame.draw.ellipse(self.image,BLUE,[0,0,20,20])
        self.mh = mh
        
        self.rect = self.image.get_rect()

        self.target = target
        
    def in_aoe(self,battle):
        return(pygame.sprite.spritecollide(self,
                                       battle.aoe_list,
                                       False,
                                       pygame.sprite.collide_circle))
                                       
    def update(self,battle):
        if((battle.player.is_alive == False) or (self.mh == False)):
            self.target = min_target(battle)
            #print("%s" % self.target.name)
            
        # If out of range, get closer
        if(len(self.in_aoe(battle))>0):
            a = self.in_aoe(battle)[0]
            sc = [self.rect.x+10,self.rect.y+10]
            sa = [a.rect.x+a.width/2,a.rect.y+a.width/2]
            diff_y = float(sc[1]-sa[1])
            diff_x = float(sc[0]-sa[0])
            theta = math.atan2(diff_y,diff_x)
            self.rect.y = int(round(self.rect.y + 2*math.sin(theta)))
            self.rect.x = int(round(self.rect.x + 2*math.cos(theta)))

        elif(dist(self,self.target)>self.range):
            diff_y = float(self.target.rect.y - self.rect.y)
            diff_x = float(self.target.rect.x - self.rect.x)
            theta = math.atan2(diff_y,diff_x)
            self.rect.y = int(round(self.rect.y + 2*math.sin(theta)))
            self.rect.x = int(round(self.rect.x + 2*math.cos(theta)))
        # If in range, have mana, and target low, then heal
        else:
            # 267 is perfect balance according to (n h r_H)/c_H = (d r_B (1-a))/c_B
            if((self.mana >= 300) and (self.target.health <= self.target.max_health - 15)):
                self.mana -= 300
                self.target.health = min(self.target.max_health, self.target.health+35)
                #print("Heal, mana now %d, tank up to %d" % (self.mana,self.target.health))
        # Mana regen
        if self.innervate_bool:
            bonus = 3
        else:
            bonus = 0
        self.mana = min(1000,self.mana+2+bonus)

    def innervate(self,battle):
        if self.innervate_ready:
            #print("innervate")
            self.innervate_bool = True
            self.innervate_ready = False
            # change innervate1 to string that varies based on caster
            if self.mh:
                pygame.time.set_timer(battle.innervate1,20000)
                pygame.time.set_timer(battle.innervate_on,5000)
            else:
                pygame.time.set_timer(battle.innervate2,20000)
                pygame.time.set_timer(battle.innervate_on2,5000)
            #text = font.render("MHI",True,BLACK)
            #screen.blit(text, [3,283])
            #pygame.display.flip()

class Boss(pygame.sprite.Sprite):
    """ This class represents the boss. """
    damage = 105
    mana = 1000
    name = "Boss"
    frozen = True
    width = 40
    def __init__(self, color,target,speed,health):
        # Call the parent class (Sprite) constructor
        super(Boss, self).__init__()
        self.image = pygame.Surface([40,40])
        self.image.fill(WHITE)
        self.image.set_colorkey(WHITE)
        pygame.draw.ellipse(self.image,color,[0,0,40,40])
        self.rect = self.image.get_rect()

        self.target = target
        self.speed = speed
        self.health = health
        self.max_health = health
    
    def new_target(self,battle):
        for tank in battle.tank_list:
            if tank.is_alive:
                return(tank)
        for melee in battle.melee_list:
            if melee.is_alive:
                return(melee)
        for healer in battle.healer_list:
            if healer.is_alive:
                return(healer)
        for caster in battle.caster_list:
            if(caster.is_alive == True):
                return(caster)
    
    def boss_attack(self,target,battle):
        if(target.health <= self.damage):
            print("%s died from boss attack!" % target.name)
            target.health = 0
            battle.all_sprites_list.remove(target)
            battle.team_list.remove(target)
            target.is_alive = False
            list_kill(target,battle)
            if(len(battle.team_list) > 0):
                target = self.new_target(battle)
        else:
                target.health -= int(round(self.damage*(1-target.armor)))    
    
    def cleave(self,battle):
        theta = f_theta(self,self.target)
        phi = math.pi/4
        for p in battle.team_list:
            if(f_theta(self,p) > theta - phi and f_theta(self,p) < theta + phi and dist(self,p) <= 25):
                self.boss_attack(p,battle)
                
    # Move boss towards target at speed
    def update(self,battle):
        self.target = self.new_target(battle)
        if(self.frozen == False):
            # If too far, move closer to target
            if(dist(self,self.target) > 25):
                diff_y = float(self.target.rect.y - self.rect.y)
                diff_x = float(self.target.rect.x - self.rect.x)
                theta = math.atan2(diff_y,diff_x)
                self.rect.y = int(round(self.rect.y + self.speed*math.sin(theta)))
                self.rect.x = int(round(self.rect.x + self.speed*math.cos(theta)))
            # Else, cleave target
            else:
                if(self.mana >= 600):
                    self.mana -= 600
                    self.cleave(battle)
        # Mana regen
        self.mana = min(1000,self.mana+5)

class AoE(pygame.sprite.Sprite):
    """ This class represents a (static, not growing) AoE effect. """
    benign = True
    radius = 55
    def __init__(self,color,width,height,damage):
        super(AoE, self).__init__()
        self.image = pygame.Surface([width,height])
        self.image.fill(WHITE)
        self.image.set_colorkey(WHITE)
        pygame.draw.ellipse(self.image,color,[0,0,width,height])
        self.rect = self.image.get_rect()
        self.damage = damage
        self.width = width
        self.height = height

    def change_color(self,color,width,height):
        pygame.draw.ellipse(self.image,color,[0,0,width,height])

class AoE_small(pygame.sprite.Sprite):
    benign = False
    def __init__(self,color,width,height,damage):
        super(AoE_small, self).__init__()
        self.image = pygame.Surface([width,height])
        self.image.fill(WHITE)
        self.image.set_colorkey(WHITE)
        pygame.draw.ellipse(self.image,color,[0,0,width,height])
        self.rect = self.image.get_rect()
        self.damage = damage
        self.width = width
        self.height = height
        self.radius = float(width)/4

class Battle(object):
    def __init__(self):
        difficulty = int(input("How much health should the boss have? "))
        self.difficulty = difficulty
    
    def initialize(self):
        # --- Create the window
        # Initialize Pygame
        pygame.init()
        
        # Set the height and width of the screen
        self.screen = pygame.display.set_mode([screen_width, screen_height])
        pygame.display.set_caption("Raid Simulator")

        # --- Sprite lists
        # This is a list of every sprite. All bosses and the player units as well.
        self.all_sprites_list = pygame.sprite.Group()
        
        # List of each boss (or add) in the game
        self.boss_list = pygame.sprite.Group()
        
        # List of each bullet
        self.bullet_list = pygame.sprite.Group()
        
        # List of each AoE effect
        self.aoe_list = pygame.sprite.Group()
        self.aoe_small_list = pygame.sprite.Group()
        
        # Lists of units
        self.team_list = pygame.sprite.Group()
        self.tank_list = pygame.sprite.Group()
        self.melee_list = pygame.sprite.Group()
        self.healer_list = pygame.sprite.Group()
        self.caster_list = pygame.sprite.Group()
    
        # Create tank
        self.player = Player()
        self.tank_list.add(self.player)
        self.team_list.add(self.player)
        self.all_sprites_list.add(self.player)
        
        # Create healer
        self.healer = Healer(self.player,True) # MH
        self.healer2 = Healer(self.player,False) # OH
        for g in ['healer_list', 'team_list', 'all_sprites_list']:
            getattr(self,g).add(self.healer)
            getattr(self,g).add(self.healer2)
        
        # Create a red boss with velocity 4 and target player
        self.boss = Boss(RED,self.player,4,self.difficulty)
        self.boss.rect.x = 350
        self.boss.rect.y = 200
        self.boss_list.add(self.boss)
        self.all_sprites_list.add(self.boss)
        
        # Create a caster with target boss
        self.caster = Caster(self.boss)
        self.caster2 = Caster(self.boss)
        self.caster3 = Caster(self.boss)
        for g in ['caster_list','team_list','all_sprites_list']:
            for u in ['caster','caster2','caster3']:
                getattr(self,g).add(getattr(self,u))
        
        # Create melee
        self.melee = Melee(self.boss)
        self.melee2 = Melee(self.boss)
        for g in ['melee_list','team_list','all_sprites_list']:
            for u in ['melee','melee2']:
                getattr(self,g).add(getattr(self,u))
        
        # Used to manage how fast the screen updates
        self.clock = pygame.time.Clock()
        
        # set positions
        self.score = 0
        self.player.rect.x = 400
        self.player.rect.y = 370
        self.healer.rect.x = 350
        self.healer.rect.y = 370
        self.caster.rect.x = 450
        self.caster.rect.y = 370
        self.caster2.rect.x = 300
        self.caster2.rect.y = 350
        self.healer2.rect.x = 250
        self.healer2.rect.y = 250
        self.caster3.rect.x = 150
        self.caster3.rect.y = 370
        self.melee.rect.x = 420
        self.melee.rect.y = 370
        self.melee2.rect.x = 380
        self.melee2.rect.y = 370
    
        # initialize game status and AOE timers/booleans
        self.done = False
        # boolean, true iff aoe is active
        self.aoe_active = False
        # Create timer to spawn a new AoE effect
        self.spawn_timer = 0
        # Timer to AoE despawn
        self.death_timer = 0
        # Timer to next boss melee
        self.boss_timer = 0
        self.boss_ready = True

        self.font = pygame.font.SysFont('Calibri', 16, True, False)
        # Set timers
        pygame.time.set_timer(pygame.USEREVENT+1,2000)
        self.innervate1 = pygame.USEREVENT+2
        self.innervate_on = pygame.USEREVENT+3
        self.innervate2 = pygame.USEREVENT+4
        self.innervate_on2 = pygame.USEREVENT+5
        self.shield_wall_on = pygame.USEREVENT+6
        self.shield_wall_cd = pygame.USEREVENT+7
        self.i = 0    
    
    # Updates the health/mana bars (heads up display)
    def update_hud(self):
        # Later on, we want to draw AoE's first and then teammates/bosses    
        self.all_sprites_list.draw(self.screen)
    
        pygame.draw.rect(self.screen,BLACK,[0,0,203,20], 2)
        pygame.draw.rect(self.screen,RED,[2,2,scale(self.player.health,self.player.max_health,203),17],0)
        
        pygame.draw.rect(self.screen, BLACK, [0,22,203,37], 2)
        pygame.draw.rect(self.screen,RED,[2,24,scale(self.healer.health,self.healer.max_health,203),17],0)
        pygame.draw.rect(self.screen,BLUE,[2,41,round(self.healer.mana/5),17],0)
        
        pygame.draw.rect(self.screen,BLACK, [0,61,203,37],2)
        pygame.draw.rect(self.screen,RED,[2,63,scale(self.healer2.health,self.healer2.max_health,203),17],0)
        pygame.draw.rect(self.screen,BLUE,[2,80,round(self.healer2.mana/5),17],0)
        
        pygame.draw.rect(self.screen,BLACK,[0,100,203,37],2)
        pygame.draw.rect(self.screen,RED,[2,102,scale(self.caster.health,self.caster.max_health,203),17],0)
        pygame.draw.rect(self.screen,BLUE,[2,119,round(self.caster.mana/5),17],0)
    
        pygame.draw.rect(self.screen,BLACK,[0,139,203,37],2)
        pygame.draw.rect(self.screen,RED,[2,141,scale(self.caster2.health,self.caster2.max_health,203),17],0)
        pygame.draw.rect(self.screen,BLUE,[2,158,round(self.caster2.mana/5),17],0)
    
        pygame.draw.rect(self.screen,BLACK,[0,178,203,37],2)
        pygame.draw.rect(self.screen,RED,[2,180,scale(self.melee.health,self.melee.max_health,203),17],0)
        pygame.draw.rect(self.screen,BLUE,[2,197,round(self.melee.mana/5),17],0)
    
        pygame.draw.rect(self.screen,BLACK,[0,217,203,37],2)
        pygame.draw.rect(self.screen,RED,[2,219,scale(self.melee2.health,self.melee2.max_health,203),17],0)
        pygame.draw.rect(self.screen,BLUE,[2,236,round(self.melee2.mana/5),17],0)
        
        pygame.draw.rect(self.screen,BLACK,[0,256,203,20],2)
        pygame.draw.rect(self.screen,RED,[2,258,scale(self.boss.health,self.boss.max_health,203),17],0)
    
        pygame.draw.rect(self.screen,BLACK,[0,278,203,screen_height-279],2)
            
        text1 = self.font.render("Tank %d" % int(round(float(self.player.health)*100/self.player.max_health)),True,BLACK)
        text2 = self.font.render("Healer 1 %d" % int(round(float(self.healer.health)*100/self.healer.max_health)),True,BLACK)
        text3 = self.font.render("Healer 2 %d" % int(round(float(self.healer2.health)*100/self.healer2.max_health)),True,BLACK)
        text4 = self.font.render("Caster 1 %d" % int(round(float(self.caster.health)*100/self.caster.max_health)),True,BLACK)
        text5 = self.font.render("Caster 2 %d" % int(round(float(self.caster2.health)*100/self.caster2.max_health)),True,BLACK)
        text6 = self.font.render("Melee 1 %d" % int(round(float(self.melee.health)*100/self.melee.max_health)),True,BLACK)
        text7 = self.font.render("Melee 2 %d" % int(round(float(self.melee2.health)*100/self.melee2.max_health)),True,BLACK)
        text8 = self.font.render("BOSS %d" % int(round(float(self.boss.health)*100/self.boss.max_health)),True,BLACK)
        self.screen.blit(text1, [85,3])
        self.screen.blit(text2, [85,24])
        self.screen.blit(text3, [85,63])
        self.screen.blit(text4, [85,102])
        self.screen.blit(text5, [85,141])
        self.screen.blit(text6, [85,180])
        self.screen.blit(text7, [85,219])
        self.screen.blit(text8, [85,260])
    
        if self.healer.innervate_ready:
            sh1 = "MH innervate up"
        else:
            sh1 = "..."
        if self.healer2.innervate_ready:
            sh2 = "OH innervate up"
        else:
            sh2 = "..."
        if self.player.shield_wall_ready:
            sh3 = "MT shield wall up"
        else:
            sh3 = "..."
            
        text9 = self.font.render(sh1,True,BLACK)
        text10 = self.font.render(sh2,True,BLACK)
        text11 = self.font.render(sh3,True,BLACK)
        self.screen.blit(text9, [3,283])
        self.screen.blit(text10,[3,303])
        self.screen.blit(text11,[3,323])
    
        cross = pygame.image.load("cross.png").convert()
        cross.set_colorkey(WHITE)
        for aoes in self.aoe_small_list:
            pygame.draw.ellipse(aoes.image,YELANGE,[0,0,aoes.width,aoes.height])
        for h in self.healer_list:
            self.screen.blit(cross,[h.rect.x+3,h.rect.y+3])
    
        if self.boss.frozen:
            text = self.font.render("Press spacebar to begin",True,BLACK)
            self.screen.blit(text, [300,250])
            text_dir = self.font.render("WASD: Move, I: OH Innervate, O: MH Innervate, J: Shield Wall",True,BLACK)
            self.screen.blit(text_dir, [500,250])
        
    def run(self):
        while not self.done:
            
            # AOE spawn mechanics
            if not self.aoe_active:
                self.spawn_timer += 5
            else:
                self.death_timer += 5
                
            if self.spawn_timer > 500 and not self.boss.frozen:
                # Reset the spawn timer
                self.spawn_timer = 0
                # Initialize AoE life timer
                self.death_timer = 0
                self.aoe_active = True
                #print("AoE active")
                area = AoE(GRAY,100,100,1)
                #area.rect.x = random.randrange(screen_width)
                #area.rect.y = random.randrange(screen_height)
                area.rect.x = self.boss.target.rect.x-40
                area.rect.y = self.boss.target.rect.y-40
                self.aoe_list.add(area)
                self.all_sprites_list.add(area)
            if self.death_timer > 500:
                area.change_color(ORANGE,100,100)
                area.benign = False
            if self.death_timer > 1500:
                self.death_timer = 0
                self.aoe_active = False
                #print("AoE inactive")
                self.aoe_list.remove(area)
                self.all_sprites_list.remove(area)
            # Boss melee timer and ready boolean 
            if not self.boss_ready:
                if self.boss_timer >= 350:
                    self.boss_ready = True
                else:
                    self.boss_timer += 5
            
            
            # --- Event Processing
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True
                # Set the speed based on the key pressed
                elif event.type == pygame.USEREVENT + 1 and not self.boss.frozen:
                    area_s = AoE_small(YELANGE,26,26,1)
                    area_s.rect.x = self.boss.rect.x+int((40-26)/2)
                    area_s.rect.y = self.boss.rect.y+int((40-26)/2)
                    area_s.benign = False
                    self.aoe_small_list.add(area_s)
                    self.aoe_list.add(area_s)
                    self.all_sprites_list.add(area_s)
                elif event.type == self.innervate_on:
                    self.healer.innervate_bool = False
                elif event.type == self.innervate1:
                    self.healer.innervate_ready = True
                    text = self.font.render("MH Inn Ready",True,BLACK)
                    print("MH Innervate up")
                    self.screen.blit(text, [3,283])
                    pygame.display.flip()
                elif event.type == self.innervate_on2:
                    self.healer2.innervate_bool = False
                elif event.type == self.innervate2:
                    self.healer2.innervate_ready = True
                    text = self.font.render("OH Inn Ready",True,BLACK)
                    print("OH Innervate up")
                    self.screen.blit(text, [3,303])
                    pygame.display.flip()
                elif event.type == self.shield_wall_on:
                    self.player.armor /= 2
                    pygame.time.set_timer(self.shield_wall_on,0)
                elif event.type == self.shield_wall_cd:
                    self.player.shield_wall_ready = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.player.changespeed(-3, 0)
                    elif event.key == pygame.K_d:
                        self.player.changespeed(3, 0)
                    elif event.key == pygame.K_w:
                        self.player.changespeed(0, -3)
                    elif event.key == pygame.K_s:
                        self.player.changespeed(0, 3)
                    elif event.key == pygame.K_i:
                        self.healer.innervate(self)
                    elif event.key == pygame.K_o:
                        self.healer2.innervate(self)
                    elif event.key == pygame.K_j:
                        self.player.shield_wall(self)
                    elif event.key == pygame.K_SPACE:
                        self.boss.frozen = False
                # Reset speed when key goes up
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.player.changespeed(3, 0)
                    elif event.key == pygame.K_d:
                        self.player.changespeed(-3, 0)
                    elif event.key == pygame.K_w:
                        self.player.changespeed(0, 3)
                    elif event.key == pygame.K_s:
                        self.player.changespeed(0, -3)
            
            # --- Game logic

            # Call the update() method on all the sprites
            for sprite in self.all_sprites_list:
                try:
                    sprite.update(battle=self)
                except:
                    sprite.update()
        
            # Calculate mechanics for each bullet
            for bullet in self.bullet_list:
        
                # See if it hit a boss
                boss_hit_list = pygame.sprite.spritecollide(bullet, self.boss_list, False)
        
                # For each boss hit, remove the bullet and add to the score
                for boss in boss_hit_list:
                    if(boss.health <= bullet.damage):
                        self.boss_list.remove(boss)
                        self.all_sprites_list.remove(boss)
                    else:
                        boss.health -= bullet.damage
                    self.bullet_list.remove(bullet)
                    self.all_sprites_list.remove(bullet)
                    self.score += 1
                    #print("Boss health=%d" % boss.health)
        
            # Calculate mechanics for each AoE effect
            for aoe in self.aoe_list:
                aoe_hit_list = pygame.sprite.spritecollide(aoe,self.team_list,False,pygame.sprite.collide_circle)
                for p in aoe_hit_list:
                    if not aoe.benign:
                        if p.health <= aoe.damage:
                            p.health = 0
                            print("%s died from AoE!" % p.name)
                            self.team_list.remove(p)
                            self.all_sprites_list.remove(p)
                            p.is_alive = False
                            p.health = 0
                            self.team_list.remove(p)
                            if(p.name == "Tank"):
                                self.tank_list.remove(p)
                            if(p.name=="Healer"):
                                self.healer_list.remove(p)
                            elif(p.name=="Caster"):
                                self.caster_list.remove(p)
                            elif(p.name == "Melee"):
                                self.melee_list.remove(p)
                            if(len(self.team_list)>0):
                                boss.target = self.boss.new_target(self)
                        else:
                            p.health -= aoe.damage
                            #print("%s health=%d" % (p.name,p.health))
            
            # --- Draw a frame

            # Clear the screen
            self.screen.fill(WHITE)
        
            # Draw all the spites
            self.update_hud()
            # Go ahead and update the screen with what we've drawn.
            pygame.display.flip()
        
            # --- Limit to 20 frames per second
            self.clock.tick(20)
            if(len(self.team_list)==0):
                print("You wiped at %d" % boss.health)
                break
            if(len(self.boss_list)==0):
                print("You win")
                break
            #caster1_dmg.append(caster.damage_dealt)
            #caster2_dmg.append(caster2.damage_dealt)
            #melee1_dmg.append(melee.damage_dealt)
            #melee2_dmg.append(melee2.damage_dealt)
        
        pygame.quit()