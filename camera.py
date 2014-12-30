#!/usr/bin/python
import pygame
import time
import subprocess
import tftutils
#
# CameraApp
#
class CameraApp(tftutils.TFTApp):
	
	def __init__(self, size, m_col, h_col, mb_col):
		tftutils.TFTApp.__init__(self, size, m_col, h_col, mb_col)
		
		self.last_img = ''
		
		self.menu_array = [
			{'title':'shutter', 'function':self.do_shutter},
			{'title':'exit', 'function':self.exit_app}
		]
	
	def on_button_change(self, dir):
		
		app = self.app_state
		menu = self.menu_state
		
		if dir == 'left':
			self.set_states(app,menu - 1)
		elif dir == 'right':
			self.set_states(app,menu + 1)
		elif dir == 'center':
			self.do_menu_option()
			
	def render_menu(self):
		
		self.menu.fill((0,0,0), (0,0,self.size[0], 18))
		startx = 5
		starty = 3
		menu = self.menu_state
		
		color = self.menu_color
		if menu == 0:
			color = self.highlight_color
		self.render_shutter_btn(color, startx, starty)
		
		color = self.menu_color
		if menu == 1:
			color = self.highlight_color
		self.render_exit_button(color,startx + 60, starty)
		
		if self.last_img != '':
			self.render_last_img()
			
		self.menu_updated = True
		
	def render_shutter_btn(self, color, sx, sy):
		sur = self.menu_font.render('shutter', 1, color)
		self.menu.blit( sur, (sx, sy) )
	
	def render_exit_button(self, color, sx, sy):
		sur = self.menu_font.render('exit', 1, color)
		self.menu.blit( sur, (self.size[0] - 30, sy) )
	
	def render_last_img(self):
		img = pygame.image.load(self.last_img)
		self.menu.blit(img, [0,18])
		
	def run_cmd(self,cmd):
		p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
		output = p.communicate()[0]
		return output
		
	def do_menu_option(self):
		option = self.menu_array[self.menu_state]['function']
		option()
			
	def do_shutter(self):
		self.last_img = '/home/pi/pydocs/pytft/picamera/' + time.strftime('%Y%m%d_%H%M%S') + '.jpg'
		cmd = 'raspistill -w 160 -h 110 -q 80 -t 10 -o ' + self.last_img
		self.run_cmd(cmd)
		self.render_menu()
	
	def update_surface(self):
		if self.menu_updated == True:
			self.surface.blit(self.menu, (0,0))
			self.menu_updated = False
		return self.surface