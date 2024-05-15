"""

A speedometer for the narrowboat.

Using a Waveshare LCD display
<https://files.waveshare.com/upload/2/2d/ILI9488_Data_Sheet.pdf>
and a Quectel L76 GPS module
<https://www.quectel.com/ProductDownload/L76-LB.html>
connected to a raspberry pi pico

Author:	Jennifer Liddle <jennifer@jsquared.co.uk>
        Jenny Bailey <jennyb@jsquared.co.uk>
        
"""

from machine import Pin,SPI,PWM, UART
import framebuf
import time
import random
from micropython import const

# Initialise the UART so we can read the NMEA of the GPS from the serial port
UARTx = const(0)
BAUDRATE = const(9600)
PICO_UART_TX_PIN=const(16)
PICO_UART_RX_PIN=const(17)
GPS = UART(UARTx,baudrate=BAUDRATE,tx=Pin(PICO_UART_TX_PIN),rx=Pin(PICO_UART_RX_PIN),timeout=100 ) 

# Initialise the LCD
LCD_DC   = const(8)
LCD_CS   = const(9)
LCD_SCK  = const(10)
LCD_MOSI = const(11)
LCD_MISO = const(12)
LCD_BL   = const(13)
LCD_RST  = const(15)

class LCD_3inch5(framebuf.FrameBuffer):

    def __init__(self):
        self.RED   =   const(0x07E0)
        self.GREEN =   const(0x001f)
        self.BLUE  =   const(0xf800)
        self.WHITE =   const(0xffff)
        self.BLACK =   const(0x0000)
        
        self.width = const(240)
        self.height = const(320)
        
        self.cs = Pin(LCD_CS,Pin.OUT)
        self.rst = Pin(LCD_RST,Pin.OUT)
        self.dc = Pin(LCD_DC,Pin.OUT)
        
    
        self.cs(1)
        self.dc(1)
        self.rst(1)
        self.spi = SPI(1,60_000_000,sck=Pin(LCD_SCK),mosi=Pin(LCD_MOSI),miso=Pin(LCD_MISO))
              
        self.buffer = bytearray(self.height * self.width * 2)
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
        self.init_display()

        
    def write_cmd(self, cmd):
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        self.cs(1)
        self.dc(1)
        self.cs(0)
        #self.spi.write(bytearray([0X00]))
        self.spi.write(bytearray([buf]))
        self.cs(1)


    def init_display(self):
        """Initialize display"""  
        self.rst(1)
        time.sleep_ms(5)
        self.rst(0)
        time.sleep_ms(10)
        self.rst(1)
        time.sleep_ms(5)
        self.write_cmd(0x21)
        self.write_cmd(0xC2)
        self.write_data(0x33)
        self.write_cmd(0XC5)
        self.write_data(0x00)
        self.write_data(0x1e)
        self.write_data(0x80)
        self.write_cmd(0xB1)
        self.write_data(0xB0)
        self.write_cmd(0x36)
        self.write_data(0x28)
        self.write_cmd(0XE0)
        self.write_data(0x00)
        self.write_data(0x13)
        self.write_data(0x18)
        self.write_data(0x04)
        self.write_data(0x0F)
        self.write_data(0x06)
        self.write_data(0x3a)
        self.write_data(0x56)
        self.write_data(0x4d)
        self.write_data(0x03)
        self.write_data(0x0a)
        self.write_data(0x06)
        self.write_data(0x30)
        self.write_data(0x3e)
        self.write_data(0x0f)
        self.write_cmd(0XE1)
        self.write_data(0x00)
        self.write_data(0x13)
        self.write_data(0x18)
        self.write_data(0x01)
        self.write_data(0x11)
        self.write_data(0x06)
        self.write_data(0x38)
        self.write_data(0x34)
        self.write_data(0x4d)
        self.write_data(0x06)
        self.write_data(0x0d)
        self.write_data(0x0b)
        self.write_data(0x31)
        self.write_data(0x37)
        self.write_data(0x0f)
        self.write_cmd(0X3A)
        self.write_data(0x55)
        self.write_cmd(0x11)
        time.sleep_ms(120)
        self.write_cmd(0x29)
        
        self.write_cmd(0xB6)
        self.write_data(0x00)
        self.write_data(0x62)
        
        self.write_cmd(0x36)
        self.write_data(0x28)
        
    def show_left(self):
        self.write_cmd(0x2A)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0xef)
        
        self.write_cmd(0x2B)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x01)
        self.write_data(0xdf)
        
        self.write_cmd(0x2C)
        
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(self.buffer)
        self.cs(1)
        
    def show_right(self):
        self.write_cmd(0x2A)
        self.write_data(0x00)
        self.write_data(0xf0)
        self.write_data(0x01)
        self.write_data(0xdf)
        
        self.write_cmd(0x2B)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x01)
        self.write_data(0xdf)
        
        self.write_cmd(0x2C)
        
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(self.buffer)
        self.cs(1)
        
    def bl_ctrl(self,duty):
        pwm = PWM(Pin(LCD_BL))
        pwm.freq(1000)
        if(duty>=100):
            pwm.duty_u16(65535)
        else:
            pwm.duty_u16(655*duty)
            
    def draw_point(self,x,y,color):
        self.write_cmd(0x2A)

        
        self.write_data((x-2)>>8)
        self.write_data((x-2)&0xff)
        self.write_data(x>>8)
        self.write_data(x&0xff)
        
        self.write_cmd(0x2B)
        self.write_data((y-2)>>8)
        self.write_data((y-2)&0xff)
        self.write_data(y>>8)
        self.write_data(y&0xff)
        
        self.write_cmd(0x2C)
        
        self.cs(1)
        self.dc(1)
        self.cs(0)
        for i in range(0,9):
            h_color = bytearray(color>>8)
            l_color = bytearray(color&0xff)
            self.spi.write(h_color)
            self.spi.write(l_color)
        self.cs(1)

# These are the line segments used to display our digits 0..9
LINE_LENGTH = const(90)
LINE_WIDTH = const(15)
CHARACTER_START_X = const(70)
CHARACTER_START_Y = const(50)

def draw_top():
    x = CHARACTER_START_X + LINE_WIDTH
    y = CHARACTER_START_Y
    LCD.fill_rect(x,y,LINE_LENGTH,LINE_WIDTH,LCD.BLACK)
    
def draw_top_left():
    x = CHARACTER_START_X
    y = CHARACTER_START_Y + LINE_WIDTH
    LCD.fill_rect(x,y,LINE_WIDTH, LINE_LENGTH, LCD.BLACK)
    
def draw_top_right():
    x = CHARACTER_START_X + LINE_LENGTH + LINE_WIDTH
    y = CHARACTER_START_Y + LINE_WIDTH
    LCD.fill_rect(x,y,LINE_WIDTH, LINE_LENGTH, LCD.BLACK)
    
def draw_middle():
    x = CHARACTER_START_X + LINE_WIDTH
    y = CHARACTER_START_Y + LINE_LENGTH + LINE_WIDTH
    LCD.fill_rect(x,y,LINE_LENGTH,LINE_WIDTH,LCD.BLACK)

def draw_bottom_left():
    x = CHARACTER_START_X
    y = CHARACTER_START_Y + LINE_LENGTH + LINE_WIDTH + LINE_WIDTH
    LCD.fill_rect(x,y,LINE_WIDTH, LINE_LENGTH, LCD.BLACK)
    
def draw_bottom_right():
    x = CHARACTER_START_X + LINE_LENGTH + LINE_WIDTH
    y = CHARACTER_START_Y + LINE_LENGTH + LINE_WIDTH + LINE_WIDTH
    LCD.fill_rect(x,y,LINE_WIDTH, LINE_LENGTH, LCD.BLACK)
    
def draw_bottom():
    x = CHARACTER_START_X + LINE_WIDTH
    y = CHARACTER_START_Y + LINE_LENGTH + LINE_LENGTH + LINE_WIDTH + LINE_WIDTH
    LCD.fill_rect(x,y,LINE_LENGTH,LINE_WIDTH,LCD.BLACK)
    
# We have a separate function to display each digit
def draw_zero():
    draw_top()
    draw_top_left()
    draw_top_right()
    draw_bottom_left()
    draw_bottom_right()
    draw_bottom()

def draw_one():
    draw_top_right()
    draw_bottom_right()
    
def draw_two():
    draw_top()
    draw_top_right()
    draw_middle()
    draw_bottom_left()
    draw_bottom()
    
def draw_three():
    draw_top()
    draw_top_right()
    draw_middle()
    draw_bottom_right()
    draw_bottom()
    
def draw_four():
    draw_top_left()
    draw_top_right()
    draw_middle()
    draw_bottom_right()
    
def draw_five():
    draw_top()
    draw_top_left()
    draw_middle()
    draw_bottom_right()
    draw_bottom()
    
def draw_six():
    draw_top()
    draw_top_left()
    draw_middle()
    draw_bottom_left()
    draw_bottom_right()
    draw_bottom()
    
def draw_seven():
    draw_top()
    draw_top_right()
    draw_bottom_right()
    
def draw_eight():
    draw_top()
    draw_top_left()
    draw_top_right()
    draw_middle()
    draw_bottom_left()
    draw_bottom_right()
    draw_bottom()
    
def draw_nine():
    draw_top()
    draw_top_left()
    draw_top_right()
    draw_middle()
    draw_bottom_right()
    
def draw_point():	# the decimal point
    LCD.fill_rect(0,230,40,40,LCD.BLACK)
    
NUMBERS = [draw_zero, draw_one, draw_two, draw_three, draw_four, draw_five, draw_six, draw_seven, draw_eight, draw_nine]

""" This was only used during testing and development
def test_numbers():
    while True:
        n = random.choice(NUMBERS)
        LCD.fill(LCD.WHITE)
        n()
        LCD.show_left()
        n = random.choice(NUMBERS)
        LCD.fill(LCD.WHITE)
        n()
        draw_point()
        LCD.show_right()
        time.sleep(1)
"""

# extract the 'number of satellites' count from the GGA sentence
def get_satellites(nmea):
    #print(nmea)
    return int(nmea.split(",")[7])

# extract the speed (in kph) from the VTG sentence, but return mph
def get_speed(nmea):
    #print(nmea)
    speed = float(nmea.split(",")[7])	# speed in k/h
    speed = speed * 0.62137119			# speed in mph
    return speed

# display a 'J2' at startup, because....well, why not?
def display_logo():
    LCD.fill(LCD.WHITE)
    draw_top()
    draw_top_right()
    draw_bottom_right()
    draw_bottom()
    draw_bottom_left()
    LCD.show_left()
    
    LCD.fill(LCD.WHITE)
    draw_two()
    LCD.show_right()
    time.sleep(5)

# Main display showing speed and number of satellites
def display_all(satellites, speed):
    if (speed >= 10):
        speed = 9.9
        
    digit = int(speed)
    LCD.fill(LCD.WHITE)
    NUMBERS[digit]()
    LCD.show_left()
    
    digit = int(speed * 10) % 10
    LCD.fill(LCD.WHITE)
    NUMBERS[digit]()
    
    for x in range(0,satellites):
        LCD.fill_rect(LCD.width-((x+1)*20),10,10,10,LCD.BLACK)
    draw_point()
    LCD.show_right()
    
if __name__=='__main__':
    opt_level(3)
    LCD = LCD_3inch5()
    LCD.bl_ctrl(100)
    #print(opt_level())
    #print(mem_info())
    
    display_logo()
    
    satellites = 0
    speed = 0
    new_satellites = 0
    new_speed = 0
    display_all(satellites,speed)

    # Read GPS, extract values, display if values have changed
    while True:
        nmea = GPS.readline()
        if (nmea):
            #print(nmea)
            try:
                nmea = nmea.decode("utf-8")
            except:
                nmea = "      "
            nmea = nmea[3:-2]
            if (nmea[0:3] == "GGA"):
                new_satellites = get_satellites(nmea)
            if (nmea[0:3] == "VTG"):
                new_speed = get_speed(nmea)

        if ( (new_speed != speed) or (new_satellites != satellites) ):
            speed = new_speed
            satellites = new_satellites
            display_all(satellites,speed)
            
