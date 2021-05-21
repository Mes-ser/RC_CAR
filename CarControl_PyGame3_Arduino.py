
### Wazne! Po co stosowac przelicznik dla wartosci wyslanej do arduino,
### jak mozna to tylko zastosowac dla
### wartosci igly (needle) i obliczac sobie z warosci 0-180
### 0-180 to zakres liczb jakie arduino przyjmuje w servo.read() odnosi się do stopni 90 to środek
import pygame
import serial
import math
import struct
import serial.tools.list_ports


print("Connect Arduino to computer...")

### konfiguracja srial###
port = ""
while(port == ""):
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if "Arduino" in p[1]:
            print("Arduino Connected!")
            port = p[0]
            break

sendToArduino = serial.Serial(port, 9600)
sendToArduino.flushInput()
przelicznik = -0.666666

### makrodefinicje kolorow ###
white = (255, 255, 255)
backgroundColor = (178, 178, 178)

### ustawienie rozdzielczości(wielkość) okna ###
display_width = 440
display_height = 440

### Inicjacja okna ###
pygame.init() # inicjacja okna
progDisplay = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Program Testowy 01') # Tytuł okna
#clock = pygame.time.Clock() # Ustawienei zegara

### Wczytanie grafik ###
tachScaleImg = pygame.image.load('images\\tach_scale.png')
tachNeedleImg = pygame.image.load('images\\tach_needle.png')

### Funkcja odpowiedzialna za obracanie obrazka wzgledem srodka ###
def rot_center(image, angle):
    """rotate an image while keeping its center and size"""
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image

# definicja igly wsaznika
def needle(r, x, y):
    progDisplay.blit(rot_center(tachNeedleImg, r),(x, y))
# definicja skali
def tachScale(x, y):
    progDisplay.blit(tachScaleImg, (x, y))


x = ((display_width * 0.5) - 220)
y = ((display_height * 0.5) - 220)

crashed = False
serWheels = -180
serMotor = 0
serWheels_change = 0
serMotor_change = 0
while not crashed:

    for event in pygame.event.get(): # Czytanie eventow
        if event.type == pygame.QUIT:
            crashed = True

        if event.type == pygame.KEYDOWN: #Sprawdzanie czy wciśniety klawisz
            if event.key == pygame.K_w: #
                serMotor_change = 1
            elif event.key == pygame.K_s:
                serMotor_change = -1

            if event.key == pygame.K_d:
                serWheels_change = 1
            elif event.key == pygame.K_a:
                serWheels_change = -1


        if event.type == pygame.KEYUP:
            if (event.key == pygame.K_d) or (event.key == pygame.K_a):
                serWheels_change = 0
            if (event.key == pygame.K_w) or (event.key == pygame.K_s):
                serMotor_change = 0

        #print(event)
    if (serWheels - serWheels_change) < -235 or (serWheels - serWheels_change) > -125:
        serWheels_change = 0
    if (serMotor + serMotor_change) < 0 or (serMotor + serMotor_change) > 180:
        serMotor_change = 0

    serWheels -= serWheels_change
    serMotor += serMotor_change

    progDisplay.fill(backgroundColor)
    tachScale(x, y)
    needle(serWheels, x, y)

    serWheelWynik = round( ( (serWheels + 45) * przelicznik ) )
    serMotorWynik = serMotor
    try:
        sendToArduino.write(struct.pack('>BB', serMotorWynik, serWheelWynik))
    except:
        print("Arduino Disconnected!")
        break
    print(str(serMotorWynik) + ' ' + str(serWheelWynik))

    pygame.display.update()
    #clock.tick(240)

pygame.quit()
sendToArduino.close()
quit()
