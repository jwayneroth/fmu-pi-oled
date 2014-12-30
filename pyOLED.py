#!/usr/bin/python
import sys
import os 
import time
import oledutils
import fmu

#
# OLED Class
# main screen, app class
#  	
class OLED:
	
	def __init__(self):
	
		self.app_state = 0
		self.menu_state = 0
		self.menu_updated = True
		
		self.fmu = fmu.FMUApp()
		
		self.menu_array = [
			{'title':'FMU', 'app':self.fmu}
		]
		
		self.current_app = None
		
		self.btns = oledutils.BTNS()
		self.btns.change += self.on_button_change
		
		self.update_menu()
		
	def on_button_change(self, dir):
		if self.app_state == 0:
			
			app = self.app_state
			menu = self.menu_state
			
			if dir == 'up':
				self.set_states(app,menu - 1)
			elif dir == 'down':
				self.set_states(app,menu + 1)
			elif dir == 'center':
				self.set_states(1,menu)
			
		else:	
			self.current_app.on_button_change(dir)
	
	def set_states(self, app, menu):
		if app > 1:
			app = 0
		elif app < 0:
			app = 1
		
		menu_max = len(self.menu_array) - 1
		if menu > menu_max:
			menu = 0
		elif menu < 0:
			menu = menu_max
			
		self.app_state = app
		self.menu_state = menu
	
		if self.app_state == 1:
			self.start_current_app()
		else:
			self.update_menu()
	
	def start_current_app(self):
		self.current_app = self.menu_array[self.menu_state]['app']
		self.current_app.exit += self.on_app_exit
		self.current_app.start_app()
		self.menu_state = 0
	
	def on_app_exit(self):
		self.current_app.exit -= self.on_app_exit
		self.current_app = None
		self.set_states(0,self.menu_state)
		
	def update_menu(self):
		self.menu.fill(self.menu_bg_color)
		self.render_menu()
		
	def render_menu(self):
		ypos = 20
		for i in range( len( self.menu_array )):
			option_name = self.menu_array[i]['title']
			if i == self.menu_state:
				self.menu.fill((0,0,0), (0, ypos, 160, self.menu_line_height ))
				sur = self.menu_font.render(option_name, 1, self.highlight_color)
			else:
				sur = self.menu_font.render(option_name, 1, self.menu_color)
			self.menu.blit( sur, (5, ypos) )
			ypos = ypos + self.menu_line_height
			
		self.menu_updated = True
		
	def update_surface(self):
		#self.background.fill((10, 10, 10))
		if self.screensaver_on == False:
			if self.app_state == 0:
				if self.menu_updated == True:
					self.background.blit(self.menu, (0,0))
					self.menu_updated = False
			else:
				current_app = self.menu_array[self.menu_state]
				self.background.blit(self.current_app.update_surface(), [0,0])
		else:
			if self.current_app == self.fmu:
				self.background.blit(self.current_app.update_surface(), [0,0])
			self.screensaver.update_surface()
			self.background.blit(self.screensaver.surface, self.screensaver.origin)
		
		self.screen.blit(self.background, (0, 0))
		pygame.display.flip()
	
	def close(self):
		pygame.quit()
		sys.exit()
		
	def run(self):
		while True:
			try:
				self.update_surface()
				time.sleep(.005)
			except KeyboardInterrupt:
				self.close()

if __name__ == "__main__" :
    game = OLED()
    game.run()