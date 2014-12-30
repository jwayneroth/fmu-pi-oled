#!/usr/bin/python
import pygame
import thread
import time
import urllib
import re
import feedparser
import tftutils
import mpc
#
# FMUApp Class
# inherits from TFTApp
#
class FMUApp():#TFTApp):
	streams = [
		{'title':'WFMU','url':'http://stream0.wfmu.org/freeform-128k'}, 
		{'title':'GtDR','url':'http://stream0.wfmu.org:80/drummer'},
		{'title':'Ichiban','url':'http://stream0.wfmu.org/ichiban'},
		{'title':'Ubu','url':'http://stream0.wfmu.org/ubu'},
		{'title':'DIY','url':'http://stream0.wfmu.org/do-or-diy'}
	]
	otherStations = [
		{'title':'wnyc','url':'http://fm939.wnyc.org/wnycfm'},
		{'title':'bbc','url':'http://am820.wnyc.org/wnycam'},
		{'title':'wqxr','url':'http://stream.wqxr.org/wqxr'},
		{'title':'q2','url':'http://q2stream.wqxr.org/q2'}
	]
	controls = [
		{'title':'play_pause','url':''},
		{'title':'volume_up','url':''},
		{'title':'volume_down','url':''},
		{'title':'seek_back','url':''},
		{'title':'seek_forward','url':''},
		{'title':'exit','url':''}
	]
	archives = []
	
	def __init__(self, size, m_col, h_col, mb_col, scroll_col, other_col, other_highlight_col):
		#TFTApp.__init__(self, size)
		self.surface = pygame.Surface(size)
		self.menu_array = [
			{'title':'controls','tracks':FMUApp.controls},
			{'title':'streams','tracks':FMUApp.streams},
			{'title':'archives','tracks':FMUApp.archives},
			{'title':'other','tracks':FMUApp.otherStations}
		]
		self.app_state = 0
		self.menu_state = 0
		self.sub_menu_state = 0
		self.back_button = False
		
		self.scroll_color = scroll_col
		self.menu_color = m_col
		self.highlight_color = h_col
		self.menu_bg_color = mb_col
		self.back_btn_color = other_col
		self.back_highlight_color = other_highlight_col
		
		self.menu_height = 98
		self.menu_width = 160
		self.menu_font_size = 16
		self.menu_line_height = 17
		self.menu_font = pygame.font.Font('/home/pi/fonts/FUTURA_N.TTF', self.menu_font_size) 
		self.menu = pygame.Surface((self.menu_width, self.menu_height))
		
		self.menu_updated = False
		self.got_archives = False
		
		#self.screensaver = tftutils.TFTScreensaver((self.menu_width, self.menu_height))
		#self.screensaver.fire += self.on_screensaver_fire
		
		self.fmu_scroll = FMUScroll(160, self.scroll_color)
		self.mpc = mpc.MPC()
		self.mpc.change += self.on_mpc_change
		
		self.url_opener = urllib.FancyURLopener({})
		
		self.exit = tftutils.EventHook()
		
	def start_app(self):
		#self.screensaver_on = False
		self.mpc.start()
		self.mpc.load_stream(FMUApp.streams[0]['url'])
		self.update_menu()
		#self.screensaver.start()
	
	#
	# on_mpc_change
	# receives evts from MPC class
	#
	def on_mpc_change(self, evt):
		if evt['type'] == 'player':
			current = self.filter_stream_name( evt['data'][0] )
			if current != self.fmu_scroll.text:
				self.fmu_scroll.update_surface( current )
			if evt['data'][2] == True:
				self.update_menu()
		elif evt['type'] == 'mixer':
			self.update_menu()
			
	#
	# on_button_change
	# called by TFT, which receives evts BTNS class
	#
	def on_button_change(self, dir):
		#self.screensaver.reset()
		#if self.screensaver_on == True:
		#	self.screensaver_on = False
		#	self.update_menu()
		#	return
		app = self.app_state
		menu = self.menu_state
		sub = self.sub_menu_state
		if dir == 'right':
			if app == 0 and menu == 0:
				self.set_states(app,menu,sub + 1)
			elif app == 1:
				self.toggleBackButton()
		elif dir == 'left':
			if app == 0 and menu == 0:
				self.set_states(app,menu,sub - 1)
			elif app == 1:
				self.toggleBackButton()
		elif dir == 'up':
			if app == 0:
				self.set_states(app,menu - 1,0)
			else:
				self.set_states(app,menu,sub - 1)
		elif dir == 'down':
			if app == 0:
				self.set_states(app,menu + 1,0)
			else:
				self.set_states(app,menu,sub + 1)
		elif dir == 'center':
			if app == 0:
				if menu == 0:
					self.do_menu_option()
				else:
					self.set_states(1,menu,0)
			else:
				if self.back_button == True:
					self.do_back_button();
				else:	
					self.do_menu_option()
	
	#
	# set_states
	# maintain the app's state vars
	#
	def set_states(self,app,menu,sub):
		if app > 1:
			app = 0
		elif app < 0:
			app = 1
		
		menu_max = len(self.menu_array) - 1
		if menu > menu_max:
			menu = 0
		elif menu < 0:
			menu = menu_max
			
		sub_max = len( self.menu_array[ self.menu_state ][ 'tracks' ] ) - 1
		if sub > sub_max:
			sub = 0
		elif sub < 0:
			sub = sub_max
		
		self.app_state = app
		self.menu_state = menu
		self.sub_menu_state = sub
		
		#print 'FMUApp:set_states:app:' + str(app) + ' menu:' + str(menu) + ' sub:' + str(sub)
		
		self.update_menu()
	
	#
	# do_menu_option
	#
	def do_menu_option(self):
		if self.menu_state == 0:
			self.do_mpc_control()
		elif self.menu_state == 2:
			self.load_archive()
		elif self.menu_state == 4:
			self.do_function()
		else:
			self.play_track()
	
	
	def do_mpc_control(self):
		title = self.menu_array[self.menu_state]['tracks'][self.sub_menu_state]['title']
		if  title == 'play_pause':
			self.mpc.toggle_pause()
		elif title == 'volume_up':
			self.mpc.set_volume(1)
		elif title == 'volume_down':
			self.mpc.set_volume(0)
		elif title == 'seek_back':
			self.mpc.seek(0)
		elif title == 'seek_forward':
			self.mpc.seek(1)
		elif title == 'exit':
			self.exit_app()
	
	def do_function(self):
		if self.menu_array[self.menu_state]['tracks'][self.sub_menu_state]['title'] == 'restart':
			self.do_restart()
	
	def load_archive(self):
		url = self.menu_array[self.menu_state]['tracks'][self.sub_menu_state]['url']
		f = self.url_opener.open( url )
		stream = f.read()
		self.mpc.load_stream(stream)
		self.set_states(0,0,0)
		
	def play_track(self):
		url = self.menu_array[self.menu_state]['tracks'][self.sub_menu_state]['url']
		self.mpc.play_track(url)
		self.set_states(0,0,0)
	
	#
	# update_menu
	# calls render of appropriate menu type
	#
	def update_menu(self):
		self.menu.fill(self.menu_bg_color)
		
		if self.app_state == 0:
			self.render_main_menu()
		else:
			self.render_sub_menu()
			
	#
	# render_main_menu
	#
	def render_main_menu(self):
		ypos = self.menu_line_height
		
		self.render_main_controls()
		
		for i in range( len(self.menu_array) - 1 ):
			option_name = self.menu_array[i+1]['title']
			if i + 1 == self.menu_state:
				self.menu.fill((0,0,0), (0, ypos, 160, self.menu_line_height ))
				sur = self.menu_font.render(option_name, 1, self.highlight_color)
			else:
				sur = self.menu_font.render(option_name, 1, self.menu_color)
			self.menu.blit( sur, (5, ypos) )
			ypos = ypos + self.menu_line_height
			
		self.menu_updated = True
	
	#
	#render_sub_menu
	#
	def render_sub_menu(self):
		
		if self.menu_array[self.menu_state]['title'] == 'archives' and self.got_archives == False:
			self.get_archives()
		
		options_per_page = 5
		page = int(self.sub_menu_state / options_per_page)
		active_index = self.sub_menu_state % options_per_page
		sub_menu = self.menu_array[self.menu_state]['tracks']
		slice_length = len( sub_menu[page * options_per_page:page * options_per_page + options_per_page] )
		
		for i in range(slice_length):
			
			ypos = i * self.menu_line_height
			option_name = sub_menu[page * options_per_page + i]['title']
			
			if i == active_index and self.back_button == False:
				self.menu.fill((0,0,0),(0,ypos,160, self.menu_line_height))
				sur = self.menu_font.render(option_name, 1, self.highlight_color)
			else:
				sur = self.menu_font.render(option_name, 1, self.menu_color)
			self.menu.blit( sur, (5, ypos) )
		
		self.render_sub_controls()
		
		self.menu_updated = True
	
	#
	# render main controls
	#
	def render_main_controls(self):
		if self.menu_state == 0:
			self.menu.fill((0,0,0),(0,0,160,self.menu_line_height))
		startx = 5
		starty = 3
		menu = self.menu_state
		color = self.menu_color
		if menu == 0 and self.sub_menu_state == 0:
			color = self.highlight_color
		self.render_play_pause(color, startx, starty)
		
		color = self.menu_color
		if menu == 0 and self.sub_menu_state == 1:
			color = self.highlight_color
		self.render_volume_up(color, startx + 20, starty)
		
		color = self.menu_color
		if menu == 0 and self.sub_menu_state == 2:
			color = self.highlight_color
		self.render_volume_down(color, startx + 40, starty)
		
		color = self.menu_color
		if menu == 0 and self.sub_menu_state == 3:
			color = self.highlight_color	
		self.render_seek_back(color, startx + 60, starty+2)
		
		color = self.menu_color
		if menu == 0 and self.sub_menu_state == 4:
			color = self.highlight_color
		self.render_seek_forward(color, startx + 80, starty+2)
		
		color = self.back_btn_color
		if menu == 0 and self.sub_menu_state == 5:
			color = self.back_highlight_color
		self.render_exit(color, startx + 100, starty+2)
		
		self.render_volume(starty)
		
	def render_play_pause(self, color, sx, sy):	
		if self.mpc.is_paused:
			pygame.draw.line(self.menu, color, [sx,sy+1],[sx,sy+10], 2)
			pygame.draw.line(self.menu,  color, [sx+5,sy+1],[sx+5,sy+10], 2)
		else:
			pygame.draw.lines(self.menu, color, 1, ([sx,sy+2],[sx+8,sy+6],[sx,sy+10]), 2)
			
	def render_volume_up(self, color, sx, sy):
		pygame.draw.line(self.menu, color, [sx,sy+5],[sx+9,sy+5], 2)
		pygame.draw.line(self.menu,  color, [sx+4,sy+1],[sx+4,sy+10], 2)
		
	def render_volume_down(self, color, sx, sy):	
		pygame.draw.line(self.menu, color, [sx,sy+5],[sx+10,sy+5], 2)
		
	def render_seek_back(self, color, sx, sy):
		pygame.draw.lines(self.menu, color, 0, ([sx+5,sy],[sx,sy+3],[sx+5,sy+6]), 2)
		
	def render_seek_forward(self, color, sx, sy):
		pygame.draw.lines(self.menu, color, 0, ([sx,sy],[sx+5,sy+3],[sx,sy+6]), 2)
	
	def render_exit(self, color, sx, sy):
		#pygame.draw.rect(self.menu, self.menu_bg_color, (sx,sy,10,10))
		pygame.draw.line(self.menu, color, [sx,sy],[sx+6,sy+6], 2)
		pygame.draw.line(self.menu,  color, [sx+6,sy],[sx,sy+6], 2)
	
	def render_volume(self, sy):
		volume = self.mpc.get_volume()
		surface = self.menu_font.render(volume, 1, self.back_btn_color)
		self.menu.blit( surface, (160 - surface.get_width() - 3, sy) )
	
	def render_sub_controls(self):
		sy = 84
		self.menu.fill((0,0,0),(0, sy, self.menu_width, self.menu_height - sy))
		self.render_back_button(sy)
	
	#
	# render_back_button
	#
	def render_back_button(self, sy):
		if self.back_button == True:
			sur = self.menu_font.render('BACK', 1, self.back_highlight_color, (0,0,0))
		else:
			sur = self.menu_font.render('BACK', 1, self.back_btn_color, (0,0,0))
		self.menu.blit( sur, (120, sy) )
	
	#def on_screensaver_fire(self):
	#	self.screensaver_on = True
			
	#
	# update_surface
	# blit FMU Scroll
	# blit menu if menu_updated flag is True
	#
	def update_surface(self):
		self.surface.fill(self.fmu_scroll.bg_color, self.fmu_scroll.display_rect)
		self.surface.blit(self.fmu_scroll.surface, [self.fmu_scroll.xpos, 0])
		#if self.screensaver_on == False:
		if self.menu_updated == True:
			self.surface.blit(self.menu, (0, 30))
			self.menu_updated = False
		#else:
		#	self.surface.blit(self.screensaver.update_surface(), (0,30))
		return self.surface
	
	def toggleBackButton(self):
		self.back_button = not self.back_button
		self.update_menu()
		
	def do_back_button(self):
		self.back_button = False
		self.set_states(0,0,0)
	
	def get_archives(self):
		full = feedparser.parse('http://www.wfmu.org/archivefeed/mp3.xml')
		for entry in full.entries:
			archive = dict()
			archive['title'] = self.filter_stream_name(entry.title)
			archive['url'] = entry.link
			FMUApp.archives.append(archive)
		self.got_archives = True
				
	def filter_stream_name(self,raw):
		rdict = {
			'WFMU Freeform Radio' : 'WFMU',
			'with ' : 'w/',
			'Give the Drummer Some' : 'GtDS',
			'Give the Drummer Radio on WFMU' : 'GtDR',
			'Rock \'n\' Soul Ichiban from WFMU' : 'Ichiban',
			'UbuWeb Radio on WFMU' :  'Ubu',
			'Radio Boredcast on WFMU' : 'Boredcast',
			'WFMU MP3 Archive: ' : ''
		}
		robj = re.compile('|'.join(rdict.keys()))
		return robj.sub(lambda m: rdict[m.group(0)], raw)
	
	def do_restart(self):
		pass
	
	def exit_app(self):
		self.app_state = 0
		self.menu_state = 0
		self.sub_menu_state = 0
		#self.screensaver.stop()
		self.mpc.stop()
		self.exit.fire()
		
#
# FMUScroll Class
# maintains the scrolling text (surface) that displays mpc current
#
class FMUScroll:
	def __init__(self, xpos, color):
		self.xpos = self.startx = xpos
		self.font = pygame.font.Font('/home/pi/fonts/FrutiIta.ttf', 20) 
		self.text = ''
		self.text_color = color
		self.bg_color = (0,0,0);
		self.surface = self.font.render(self.text, 1, self.text_color)
		self.display_rect = (0,0,160,30)
		self.text_rect = self.surface.get_rect()
		
		self.start_scroll_thread()
		
	def start_scroll_thread(self):
		try:
			self.thread = thread.start_new_thread( self.scroll, ())
		except:
		   print "Error: FMUScroll unable to start thread"

	def update_surface(self, text):
		self.text = text
		self.surface = self.font.render(self.text, 1, self.text_color)
		self.text_rect = self.surface.get_rect()
		self.xpos = self.startx + 1
		return self.surface
	
	def scroll(self):
		while 1:
			self.xpos -= 1
			if self.xpos <= -self.text_rect.right:
				self.xpos = self.startx
			time.sleep(.008)
