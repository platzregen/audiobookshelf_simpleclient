import xbmcgui
import xbmcaddon
import xbmc
import requests
import json
import threading
from library_service import AudioBookShelfLibraryService

class AudioBookPlayer(xbmcgui.WindowXMLDialog):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.id = kwargs['id']
		self.title = kwargs['title']
		self.cover = kwargs['cover']
		self.description = kwargs['description']
		self.narrator_name = kwargs['narrator_name']
		self.published_year = kwargs['published_year']
		self.publisher = kwargs['publisher']
		self.duration = kwargs['duration']
		self.player = xbmc.Player()
		self.library_service = AudioBookShelfLibraryService()
		self.chapters = self.library_service.get_chapters(self.id)
		self.threads = []

	def onInit(self):
		controls_mapping = {
			1: self.title,
			2: self.description,
			3: self.cover,
			4: self.narrator_name,
			5: self.published_year,
			6: self.publisher
		}
		for control_id, value in controls_mapping.items():
			control = self.getControl(control_id)
			if control_id in [1, 4, 5, 6]:  # Label controls
				control.setLabel(value)
			elif control_id == 2:  # Textbox control
				control.setText(value)
			elif control_id == 3:  # Image control
				control.setImage(value)

		self.button_controls = [
			self.getControl(1003), self.getControl(1002),
			self.getControl(1001), self.getControl(1010), self.getControl(1007),
			self.getControl(1008)
		]

		self.set_button_navigation()
		if self.button_controls:
			self.setFocus(self.button_controls[2])

	def set_button_navigation(self):
		for index, button in enumerate(self.button_controls):
			left_button = self.button_controls[index - 1] if index > 0 else button
			right_button = self.button_controls[index + 1] if index < len(self.button_controls) - 1 else button
			button.setNavigation(button, button, left_button, right_button)

	def update_progressbar(self):
		time = self.player.getTime()
		duration = self.duration
		progress_percentage = 0.0

		if not self.player.isPlaying():
			pass
		else:
			time = self.player.getTime()
			duration = self.duration
			progress_percentage = (time / duration) * 100 if duration != 0 else 0

		pb = self.getControl(1009)
		pb.setPercent(progress_percentage)

	def progressbar_updater(self):
		while self.player.isPlayingAudio():
			self.update_progressbar()
			xbmc.sleep(5000)

	def chapter_updater(self):
		while self.player.isPlayingAudio():
			self.update_chapter(self.player.getTime())
			xbmc.sleep(2000)				

	def get_chapter_by_time(self,time):
		for chapter in self.chapters:
			if chapter['start'] <= time <= chapter['end']:
				return chapter
		return None

	def update_chapter(self,time):
		current_chapter = self.get_chapter_by_time(time)
		ccontrol = self.getControl(1011)
		ccontrol.setLabel(current_chapter['title'])

	def get_next_chapter(self, time):
		current_chapter = None
		for chapter in self.chapters:
			if chapter['start'] <= time <= chapter['end']:
				current_chapter = chapter
				break
		if current_chapter and self.chapters.index(current_chapter) < len(self.chapters) - 1:
			return self.chapters[self.chapters.index(current_chapter) + 1]
		return None

	def get_previous_chapter(self, time):
		current_chapter = None
		for chapter in self.chapters:
			if chapter['start'] <= time <= chapter['end']:
				current_chapter = chapter
				break
		if current_chapter and self.chapters.index(current_chapter) > 0:
			return self.chapters[self.chapters.index(current_chapter) - 1]
		return None

	def update_timer(self):
		while self.player.isPlayingAudio():
			ct = self.player.getTime()
			
			# Umwandlung von Sekunden in Minuten und Sekunden
			minutes = int(ct // 60)
			seconds = int(ct % 60)

			# Formatierung der Ausgabe als MM:SS
			formatted_time = "{:02d}:{:02d}".format(minutes, seconds)

			timer_control = self.getControl(1012)
			timer_control.setLabel(formatted_time)        
			xbmc.sleep(500)	

	def _start_thread(self, target):
		thread = threading.Thread(target=target)
		thread.start()
		self.threads.append(thread)

	def onAction(self, action):
		if action.getId() == xbmcgui.ACTION_NAV_BACK:
			if self.player.isPlayingAudio():
				self.player.stop()
			self.close()
		elif action == xbmcgui.ACTION_SELECT_ITEM:
			focus_id = self.getFocusId()
			if focus_id == 1001:  # Play Button
				play_button = self.getControl(1001)
				afile = self.library_service.get_file_url(self.id)

				if self.player.isPlayingAudio():
					self.player.pause()
				else:
					self.player.play(afile)

				while not self.getControl(1010).isVisible():
					xbmc.sleep(1000)
				self.setFocus(self.getControl(1010))

				self.update_chapter(self.player.getTime())
				self._start_thread(self.progressbar_updater)
				self._start_thread(self.chapter_updater)
				self._start_thread(self.update_timer)

			elif focus_id == 1010:  # Pause Button
				self.player.pause()

				while not self.getControl(1001).isVisible():
					xbmc.sleep(1000)
				self.setFocus(self.getControl(1001))

			elif focus_id in [1003, 1008]:  # Chapter navigation buttons
				chapter = None
				if focus_id == 1003:
					chapter = self.get_previous_chapter(self.player.getTime())
				elif focus_id == 1008:
					chapter = self.get_next_chapter(self.player.getTime())
				
				if chapter:
					cs = chapter['start']
					self.player.seekTime(cs)

			elif focus_id in [1002, 1007]:  # Time navigation buttons
				ct = self.player.getTime()
				st = None
				if focus_id == 1002:
					st = ct - 10
				elif focus_id == 1007:
					st = ct + 10

				if st is not None:
					self.player.seekTime(st)

	def close(self):
		if self.player.isPlayingAudio():
			self.player.stop()

		for thread in self.threads:
			if thread.is_alive():
				thread.join(timeout=2)

		super().close()		
				
					
if __name__ == "__main__":
	if "play" in sys.argv:
		xbmcgui.Dialog().notification('Audiobook Player', 'Play Funktion hier!', xbmcgui.NOTIFICATION_INFO, 2000)
	else:
		myDialog = AudioBookPlayer('audiobook_dialog.xml', xbmcaddon.Addon().getAddonInfo('path'))
		myDialog.doModal()
		del myDialog
