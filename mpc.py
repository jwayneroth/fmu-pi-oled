#!/usr/bin/python
import thread
import time
import subprocess
import tftutils
#
# MPC class
# maintains a thread listening for mpc changes
#
class MPC:
	def __init__(self):
		self.is_paused = False
		self.volume = self.run_cmd('mpc volume')[7:10].strip()
		self.change = tftutils.EventHook()

	def start(self):
		self.stop_flag = False
		self.startListener()
	
	def stop(self):
		self.stop_flag = True
				
	def run_cmd(self,cmd):
		p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
		output = p.communicate()[0]
		return output
	
	def seek(self,forward):
		if forward:
			self.run_cmd('mpc seek +5%')
		else:
			self.run_cmd('mpc seek -5%')
			
	def set_volume(self,up):
		if up:
			self.run_cmd( 'mpc volume +2' )	
		else:
			self.run_cmd( 'mpc volume -2' )
	
	def get_volume(self):
		return self.volume
		
	def toggle_pause(self):
		if self.is_paused == 1:
			self.run_cmd('mpc play')
		else:
			self.run_cmd('mpc pause')
	
	def load_stream(self, url):
		self.run_cmd('mpc clear')
		self.run_cmd('mpc add ' + url)
		self.run_cmd('mpc play')
		self.run_cmd('mpc current')
	
	def play_track(self,url):
		self.run_cmd('mpc clear')
		self.run_cmd('mpc add ' + url)
		self.run_cmd('mpc play')
	
	def startListener(self):
		try:
			self.thread = thread.start_new_thread( self.get_stats, ())
			return thread
		except:
		   print "Error: MPC unable to startListener"
		   
	def get_stats(self):
		while 1:
			change = self.run_cmd('mpc idle player mixer')	
			if change.strip() == 'player':
				current = self.run_cmd( 'mpc current')
				status = self.run_cmd('mpc status')
				lines = status.splitlines()
				pause_change = False
				if len(lines) > 1:
					line_two_status = lines[1][lines[1].find('[')+1:lines[1].find(']')]
					if line_two_status == 'paused' and self.is_paused == False:
						self.is_paused = True
						pause_change = True
					elif line_two_status == 'playing' and self.is_paused == True:
						self.is_paused = False
						pause_change = True
				self.change.fire({'type' : 'player', 'data': [current,status,pause_change]})
			elif change.strip() == 'mixer':
				self.volume = self.run_cmd('mpc volume')[7:10].strip()
				self.change.fire({'type':'mixer', 'data': [self.volume]})

