import pygame
import random
import time
import threading
import sys

# Constants
defaultRed = 150
defaultYellow = 5
defaultGreen = 20
defaultMinimum = 10
defaultMaximum = 60

signals = []
noOfSignals = 4
currentGreen = 0
currentYellow = 0
nextGreen = (currentGreen + 1) % noOfSignals

speeds = {'car': 2.25, 'bus': 1.8, 'truck': 1.8, 'rickshaw': 2, 'bike': 2.5}
vehicles = {'right': {0:[], 1:[], 2:[], 'crossed':0}, 
           'down': {0:[], 1:[], 2:[], 'crossed':0}, 
           'left': {0:[], 1:[], 2:[], 'crossed':0}, 
           'up': {0:[], 1:[], 2:[], 'crossed':0}}

x = {'right':[0,0,0], 'down':[755,727,697], 'left':[1400,1400,1400], 'up':[602,627,657]}    
y = {'right':[348,370,398], 'down':[0,0,0], 'left':[498,466,436], 'up':[800,800,800]}

vehicleTypes = {0:'car', 1:'bus', 2:'truck', 3:'rickshaw', 4:'bike'}
directionNumbers = {0:'right', 1:'down', 2:'left', 3:'up'}

signalCoods = [(530,230), (810,230), (810,570), (530,570)]
signalTimerCoods = [(530,210), (810,210), (810,550), (530,550)]

stopLines = {'right': 590, 'down': 330, 'left': 800, 'up': 535}
defaultStop = {'right': 580, 'down': 320, 'left': 810, 'up': 545}
stops = {'right': [580,580,580], 'down': [320,320,320], 'left': [810,810,810], 'up': [545,545,545]}

simulation = pygame.sprite.Group()

class TrafficSignal:
    def __init__(self, red, yellow, green, minimum, maximum):
        self.red = red
        self.yellow = yellow
        self.green = green
        self.minimum = minimum
        self.maximum = maximum
        self.signalText = "30"

class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicleClass, direction_number, direction, will_turn):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        self.vehicleClass = vehicleClass
        self.speed = speeds[vehicleClass]
        self.direction_number = direction_number
        self.direction = direction
        self.x = x[direction][lane]
        self.y = y[direction][lane]
        self.crossed = 0
        self.willTurn = will_turn
        self.turned = 0
        vehicles[direction][lane].append(self)
        self.index = len(vehicles[direction][lane]) - 1
        path = f"images/{direction}/{vehicleClass}.png"
        self.originalImage = pygame.image.load(path)
        self.currentImage = self.originalImage
        simulation.add(self)
        
        if direction == 'right':
            if len(vehicles[direction][lane]) > 1 and not vehicles[direction][lane][self.index-1].crossed:
                self.stop = vehicles[direction][lane][self.index-1].stop - vehicles[direction][lane][self.index-1].currentImage.get_rect().width - 15
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().width + 15    
            x[direction][lane] -= temp
            stops[direction][lane] -= temp
        elif direction == 'left':
            if len(vehicles[direction][lane]) > 1 and not vehicles[direction][lane][self.index-1].crossed:
                self.stop = vehicles[direction][lane][self.index-1].stop + vehicles[direction][lane][self.index-1].currentImage.get_rect().width + 15
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().width + 15
            x[direction][lane] += temp
            stops[direction][lane] += temp
        elif direction == 'down':
            if len(vehicles[direction][lane]) > 1 and not vehicles[direction][lane][self.index-1].crossed:
                self.stop = vehicles[direction][lane][self.index-1].stop - vehicles[direction][lane][self.index-1].currentImage.get_rect().height - 15
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().height + 15
            y[direction][lane] -= temp
            stops[direction][lane] -= temp
        elif direction == 'up':
            if len(vehicles[direction][lane]) > 1 and not vehicles[direction][lane][self.index-1].crossed:
                self.stop = vehicles[direction][lane][self.index-1].stop + vehicles[direction][lane][self.index-1].currentImage.get_rect().height + 15
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().height + 15
            y[direction][lane] += temp
            stops[direction][lane] += temp

    def move(self):
        global currentGreen, currentYellow
        if self.direction == 'right':
            if not self.crossed and self.x + self.currentImage.get_rect().width > stopLines[self.direction]:
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
            if ((self.x + self.currentImage.get_rect().width <= self.stop or self.crossed == 1 or 
                (currentGreen == 0 and currentYellow == 0)) and 
                (self.index == 0 or self.x + self.currentImage.get_rect().width < 
                (vehicles[self.direction][self.lane][self.index-1].x - 15))):
                self.x += self.speed
        elif self.direction == 'left':
            if not self.crossed and self.x < stopLines[self.direction]:
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
            if ((self.x >= self.stop or self.crossed == 1 or 
                (currentGreen == 2 and currentYellow == 0)) and 
                (self.index == 0 or self.x > 
                (vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().width + 15))):
                self.x -= self.speed
        elif self.direction == 'down':
            if not self.crossed and self.y + self.currentImage.get_rect().height > stopLines[self.direction]:
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
            if ((self.y + self.currentImage.get_rect().height <= self.stop or self.crossed == 1 or 
                (currentGreen == 1 and currentYellow == 0)) and 
                (self.index == 0 or self.y + self.currentImage.get_rect().height < 
                (vehicles[self.direction][self.lane][self.index-1].y - 15))):
                self.y += self.speed
        elif self.direction == 'up':
            if not self.crossed and self.y < stopLines[self.direction]:
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
            if ((self.y >= self.stop or self.crossed == 1 or 
                (currentGreen == 3 and currentYellow == 0)) and 
                (self.index == 0 or self.y > 
                (vehicles[self.direction][self.lane][self.index-1].y + vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().height + 15))):
                self.y -= self.speed

def initialize():
    ts1 = TrafficSignal(0, defaultYellow, defaultGreen, defaultMinimum, defaultMaximum)
    signals.append(ts1)
    ts2 = TrafficSignal(ts1.red+ts1.yellow+ts1.green, defaultYellow, defaultGreen, defaultMinimum, defaultMaximum)
    signals.append(ts2)
    ts3 = TrafficSignal(defaultRed, defaultYellow, defaultGreen, defaultMinimum, defaultMaximum)
    signals.append(ts3)
    ts4 = TrafficSignal(defaultRed, defaultYellow, defaultGreen, defaultMinimum, defaultMaximum)
    signals.append(ts4)
    repeat()

def repeat():
    global currentGreen, currentYellow, nextGreen
    while signals[currentGreen].green > 0:
        updateValues()
        time.sleep(1)
    currentYellow = 1
    while signals[currentGreen].yellow > 0:
        updateValues()
        time.sleep(1)
    currentYellow = 0
    currentGreen = nextGreen
    nextGreen = (currentGreen + 1) % noOfSignals
    signals[nextGreen].red = signals[currentGreen].yellow + signals[currentGreen].green
    repeat()

def updateValues():
    for i in range(noOfSignals):
        if i == currentGreen:
            if currentYellow == 0:
                signals[i].green -= 1
            else:
                signals[i].yellow -= 1
        else:
            signals[i].red -= 1

def generateVehicles():
    while True:
        vehicle_type = random.randint(0, 4)
        lane_number = 0 if vehicle_type == 4 else random.randint(1, 2)
        will_turn = 1 if (lane_number == 2 and random.randint(0, 4) <= 2) else 0
        direction_number = random.randint(0, 3)
        Vehicle(lane_number, vehicleTypes[vehicle_type], direction_number, directionNumbers[direction_number], will_turn)
        time.sleep(1)

pygame.init()
screen = pygame.display.set_mode((1400, 800))
pygame.display.set_caption("Traffic Management System")
background = pygame.image.load('images/mod_int.png')

redSignal = pygame.image.load('images/signals/red.png')
yellowSignal = pygame.image.load('images/signals/yellow.png')
greenSignal = pygame.image.load('images/signals/green.png')
font = pygame.font.Font(None, 30)

thread2 = threading.Thread(name="initialization", target=initialize, args=())
thread2.daemon = True
thread2.start()

thread3 = threading.Thread(name="generateVehicles", target=generateVehicles, args=())
thread3.daemon = True
thread3.start()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    screen.blit(background, (0, 0))
    for i in range(noOfSignals):
        if i == currentGreen:
            if currentYellow:
                screen.blit(yellowSignal, signalCoods[i])
            else:
                screen.blit(greenSignal, signalCoods[i])
        else:
            screen.blit(redSignal, signalCoods[i])
    
    for vehicle in simulation:
        screen.blit(vehicle.currentImage, [vehicle.x, vehicle.y])
        vehicle.move()
        
    pygame.display.update()
