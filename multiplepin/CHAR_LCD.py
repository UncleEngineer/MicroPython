#================================================================
###  LCD CHARACTER DISPLAY
#     version 0.2 
#    Released under 
##  CONTROL LIBRARY FOR THE PYBOARD
#  Tested on PyBoard v1.1  running micropython.
#   (http://www.micropython.org)
##
#
# TESTED LCDs:
#    - Generic 16x2 green character display
#    - Adafruit standard 20x4 blue character LCD 
# 
# Compatibility:
#    - Any LCD chipset compatible with the Hitachi HDD44780
#
#
##  This module should give you a pretty self-contained
#  set of functions for writing text to a character LCD
# display of the standard 8-bit-parallel input kind.  
#
# This is a library of functions.  Not a class.  It would be 
# unnecessary to make this a class, and would complexify 
# the usage for hobbyists.
# 
#  This library ASSUMES you are using PyBoard pins  X1-X8  to
#  communicate to the LCD display. 
#
#
#  Requires:    pyb  module;  stm  module.
#
#Features Implemented:
#          -CLEAR / RESET the display
#          -multiple sizes (e.g. 16x2  or 20x4)
#          -user specified command & latch pins
#          -change to command mode or input mode
#          -LOCATE cursor anywhere on the screen.
#          -WRITE an ASCII character
#          -WRITE a string
#          -WRITE a full line of text
#
#Not Implemented:  
#         -Scrolling 
#         -Changing the text viewport in memory
#         -Custom LCD characters
#         -Serial in / out from character display
#         -READ from character display
#
# KNOWN ISSUES:
#   - (Minor) clear_display() and reset_display() do not show consistent
#  behavior for all displays.
#
#   - (Minor) Sometimes you must call reset_display() twice  (in a row)
#   to get the desired behavior.
#
#
### ===========================================================
#
#The MIT License (MIT)
#
#Copyright (c) 2016 K. McKenzie
#
#Permission is hereby granted, free of charge, to any person obtaining a copy of 
#this software and associated documentation files (the "Software"), to deal in 
#the Software without restriction, including without limitation the rights to 
#use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies 
#of the Software, and to permit persons to whom the Software is furnished to do 
#so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all 
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
#SOFTWARE.
#

import pyb  #For pin init and individual pin control
import stm  #For GPIOA direct port access

#Display size parameters.
# SET THESE TO YOUR DISPLAY SIZE
# USING init_size 
DISPLAY_ROWS = 2
DISPLAY_COLS = 16   #0 to 15



### EXAMPLE CODE FOR USING THIS LIBRARY:
#    1.   import LCD as lcd
#    2.   lcd.init_size(4,20)    # for a 4 line 20 col display
#         lcd.init_pins('Y9','Y10')
#    3.   lcd.reset_display()
#         lcd.clear_display()
#    4.   lcd.write_display("Hello world!")
#  You can lcd.locate(line, col)  and print a message anywhere too.


#Tells CHAR_LCD what size your display is.
#E.g.  4  by 20 or  2 by 16.
def init_size(ROWS,COLS):
    global DISPLAY_ROWS 
    global DISPLAY_COLS 

    DISPLAY_ROWS = ROWS
    DISPLAY_COLS = COLS
    return


#init_pins:  Tells CHAR_LCD  which pins on the PYBOARD will be used for
# CMD/input mode control and for latching input.  (In the example
# setup presented here  these are  'Y9' and 'Y10' respectively.  If 
# you have built the circuit shown in the Fritzing diagram then use
# those values.
def init_pins(CMDpin, ENpin):
    ''' Sets up which pin will be used as mode flag (CMD/input) and 
    which pin will latch input (1->0 to latch, then 1 again).  Since we will use 
    pins X1 - X8  (GPIOA least sig byte, A0 - A7) for the input byte, 
    it must be other pins.  Specify using a string, like 'Y9' or 'X12' etc.
    The CMDpin is connected to the RS input of the display, usu. pin 4
    The ENpin is connected to the E input of the display, usu. pin 6.
    We assume the R/W input has been tied low for W mode all the time.    
    '''
    #CMDPin and ENpin can be any valid pins available 
    #and enumerated on the PyBoard, of course.
    global CMDFlag
    global ENFlag
    CMDFlag = pyb.Pin(CMDpin)
    ENFlag = pyb.Pin(ENpin)
    # Set output byte on GPIOA:
    pyb.Pin(pyb.Pin.cpu.A0, pyb.Pin.OUT_PP) 
    pyb.Pin(pyb.Pin.cpu.A1, pyb.Pin.OUT_PP)     
    pyb.Pin(pyb.Pin.cpu.A2, pyb.Pin.OUT_PP)     
    pyb.Pin(pyb.Pin.cpu.A3, pyb.Pin.OUT_PP)       
    pyb.Pin(pyb.Pin.cpu.A4, pyb.Pin.OUT_PP)     
    pyb.Pin(pyb.Pin.cpu.A5, pyb.Pin.OUT_PP)
    pyb.Pin(pyb.Pin.cpu.A6, pyb.Pin.OUT_PP)
    pyb.Pin(pyb.Pin.cpu.A7, pyb.Pin.OUT_PP)
    pyb.Pin(pyb.Pin.cpu.A13, pyb.Pin.OUT_PP)     
    pyb.Pin(pyb.Pin.cpu.A14, pyb.Pin.OUT_PP)     
    pyb.Pin(pyb.Pin.cpu.A15, pyb.Pin.OUT_PP) 
    #Set the control pins for pull-up since latching of input
    #(E) occurs on the 1->0 transition and a floating CMD
    #pin (RS) is not desirable.  
    CMDFlag.init(mode=pyb.Pin.OUT_PP, pull=pyb.Pin.PULL_UP)
    ENFlag.init(mode=pyb.Pin.OUT_PP, pull=pyb.Pin.PULL_UP)
    

#Enter command mode to control the display's
#parameters, cursor location, reset it, etc.
def cmd_mode():
    CMDFlag.value(0)
    return

#Enter text-input mode to display 
#messages.
def input_mode():
    CMDFlag.value(1)
    return

#Latch the input byte into the display
def latch_input():
    ENFlag.value(0)
    pyb.delay(1)
    ENFlag.value(1)
    return

#Clears the display.
#NOTE If this doesn't work for you, try reset_display()
def clear_display():
    '''clear_display()   Clear the display. '''
    cmd_mode()
    #Reset display / clear 
    stm.mem16[stm.GPIOA + stm.GPIO_ODR] = 0x0001
    latch_input()
    #Set the cursor home
    stm.mem16[stm.GPIOA + stm.GPIO_ODR] = 0x0002
    latch_input()
    return


#Reset the display / put cursor at home.
#NOTE If this doesn't work for you, try  clear_display()
def reset_display():
    '''reset_display()   Resets the display / go back to cursor home'''
    cmd_mode()
    #Turn on display
    stm.mem16[stm.GPIOA + stm.GPIO_ODR] = 0x000F
    latch_input()
    #Reset display / clear
    stm.mem16[stm.GPIOA + stm.GPIO_ODR] = 0x0001
    latch_input()    
    #Set the cursor home
    stm.mem16[stm.GPIOA + stm.GPIO_ODR] = 0x0002
    latch_input()
    #Set normal 2-line display mode
    stm.mem16[stm.GPIOA + stm.GPIO_ODR] = 0x0038
    latch_input()
    # WE LEAVE THE DISPLAY IN COMMAND MODE.
    return

#Write a single ASCII character (byte) to the display.
def write_character(hexbyte):
    '''write_character(hexbyte)
    Writes a single ASCII character to the display.
    hexbyte is must be of the form 0x00NN  where NN are the
    2 bytes specifying the ASCII character to write.'''
    input_mode()
    stm.mem16[stm.GPIOA + stm.GPIO_ODR] = hexbyte
    latch_input()
    return
    
#Send a command to the display.
def command(hexbyte):
    '''command(hexbyte)
    Sends a raw command to the display.'''
    cmd_mode()
    stm.mem16[stm.GPIOA + stm.GPIO_ODR] = hexbyte
    latch_input()
    return

#Position the cursor on the display!
#IMPORTANT.  
#LINES BEGIN FROM 1
#COLUMNS BEGIN FROM 0  
def locate(line, position):
    '''locate(line,position)
    line may go from 1 to DISPLAY_ROWS. 
    position may go from 0 to DISPLAY_COLS-1'''
    global DISPLAY_ROWS
    global DISPLAY_COLS

    if line < 1:
	line = 1
       
    if line > DISPLAY_ROWS:
        line = DISPLAY_ROWS

    if position < 0 or position >= DISPLAY_COLS:
        return

    L1 = 0x0080
    L2 = L1 + 0x0040
    XT = DISPLAY_COLS  

   # IMPORTANT NOTE -- THE SECRET OF LOCATING ON A 4 LINE DISPLAY!!!!
   ## ----------------------------------------------------------------
   #The reality is that 4-line displays are just 2-line displays where the lines
   #wrap around funny.  The first line wraps to the third.  The second line 
   #wraps to the fourth.  So locating the cursor is a non obvious operation.
   #To locate to the third line on a 20 character display you add 20 to the
   #L1  position.  TO locate to the fourth line you add 20 to the L2 position,
   #for instance. 

    cmd_mode()
    if line == 1:
        stm.mem16[stm.GPIOA + stm.GPIO_ODR] = L1 + position
        latch_input()
        return
    elif line == 2:
        stm.mem16[stm.GPIOA + stm.GPIO_ODR] = L2 + position
        latch_input()
        return
    elif line ==3:
        stm.mem16[stm.GPIOA + stm.GPIO_ODR] = L1 + XT + position
        latch_input()
        return
    elif line == 4:
        stm.mem16[stm.GPIOA + stm.GPIO_ODR] = L2 + XT + position
        latch_input()
        return
    else:
        return
 
    
#Write a string to the display.  Will move the cursor off of the screen 
#if the cursor position exceeds DISPLAY_ROWS.  This will NOT cause 
#an error, however.  
def write_display(inputstr):
    '''write_display(inputstr)
    Erases the display then writes a string to the screen.  If string extends farther than the columns available in the line you should expect the cursor
    to go offscreen.  If string >= DISPLAY_COLS then cursor will be
    relocated to the beginning of the next line (if available) or to 
    the beginning of the first line.'''
    # THIS ERASES THE DISPLAY!!
    reset_display()
    i = 0
    line = 1
    for char in inputstr:
        write_character(ord(char))
        i+=1
        if i > DISPLAY_COLS:
            line += 1
            locate(line,0)
            i = 0
        if line > DISPLAY_ROWS:
            line = 1
            locate(line,0)
            i = 0
    
#Write a whole line to the display.
def write_line(line, inputstr):
    '''write_line(line, inputstr)
    write a whole line to the display.'''
    i=0
    line=line
    locate(line,0)
    for char in inputstr:
        write_character(ord(char))
        i+=1
        if i > DISPLAY_COLS:
            line += 1
            locate(line,0)
            i = 0
        if line > DISPLAY_ROWS:
            line = 1
            locate(line,0)
            i = 0


