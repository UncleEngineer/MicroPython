import CHAR_LCD as lcd

lcd.init_pins('Y9','Y10')

lcd.reset_display()
# A second reset is sometimes necessary.
lcd.reset_display() 
lcd.clear_display()

#Tell the module how big our display is.
# E.g.  2x16  or  4x20
lcd.init_size(4,16)

#Locate cursor and write a character.
#lcd.locate(2,5)
#lcd.write_character(0x23)

#Write a line of text.
lcd.write_line(1,'     HELLO')
lcd.write_line(2,' Uncle Engine
