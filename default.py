import os
import xbmc
import xbmcgui
import xbmcaddon
from login_service import AudioBookShelfService
from library_service import AudioBookShelfLibraryService
#from media_item import Audiobook
from audio_book import AudioBookPlayer

MAX_COLUMNS = 3
MAX_ROWS = 2
MAX_PER_PAGE = MAX_COLUMNS * MAX_ROWS
COVER_WIDTH = 200
COVER_HEIGHT = 200
HORIZONTAL_PADDING = 50
VERTICAL_PADDING = 50

ADDON = xbmcaddon.Addon()

CWD = ADDON.getAddonInfo('path')
ERROR_MSG = "Fehler"


class SettingsDialog(xbmcgui.Dialog):
	def get_input(self, title):
		return xbmcgui.Dialog().input(title)

	def get_and_store_settings(self):
		ip = self.get_input("Enter IP Address")
		ADDON.setSetting("ipaddress", ip)

		port = self.get_input("Enter Port")
		ADDON.setSetting("port", port)

		username = self.get_input("Enter Username")
		ADDON.setSetting("username", username)

		password = self.get_input("Enter Password")
		ADDON.setSetting("password", password)


class GUI(xbmcgui.WindowXML):
	def __init__(self, *args, **kwargs):
		self.audiobooks = kwargs.get("optional1", [])
		self.page = 0
		self.button_controls = []
		self.play_controls = []
		self.prev_button = None
		self.next_button = None
		self.last_row = False
		self.selected_index = None

	def onInit(self):
		self.set_background()
		self.display_audiobooks()

	def clear_audiobooks(self):
		for button in self.button_controls:
			self.removeControl(button)
		for play_control in self.play_controls:
			self.removeControl(play_control)

		# Entfernen der prev und next Buttons, wenn sie existieren
		if hasattr(self, 'prev_button') and self.prev_button:
			self.removeControl(self.prev_button)
			self.prev_button = None

		if hasattr(self, 'next_button') and self.next_button:
			self.removeControl(self.next_button)
			self.next_button = None

		# Listen leeren
		self.button_controls = []
		self.play_controls = []

	def set_background(self):
		bg_path = os.path.join(CWD, 'resources', 'skins', 'default', 'media', 'background.png')
		background_control = xbmcgui.ControlImage(0, 0, 1920, 1080, bg_path)
		self.addControl(background_control)

	def display_audiobooks(self):
		self.clear_audiobooks()
		self.audiobooks_to_display = self.audiobooks[self.page * MAX_PER_PAGE: (self.page + 1) * MAX_PER_PAGE]
		total_width_for_books = MAX_COLUMNS * COVER_WIDTH + (MAX_COLUMNS - 1) * HORIZONTAL_PADDING
		start_x = (1920 - total_width_for_books) // 2

		total_height_for_books = MAX_ROWS * COVER_HEIGHT + (MAX_ROWS - 1) * VERTICAL_PADDING
		start_y = (1080 - total_height_for_books) // 2

		self.create_audiobook_buttons(start_x, start_y)
		self.set_audiobook_navigation()
		
		if self.button_controls:
			self.setFocus(self.button_controls[0])

	def create_audiobook_buttons(self, start_x, start_y):
		addon_dir = xbmcaddon.Addon().getAddonInfo('path')
		play_path = os.path.join(addon_dir, 'resources', 'skins', 'default', 'media', 'play.png')

		for row in range(MAX_ROWS):
			for column in range(MAX_COLUMNS):
				index = row * MAX_COLUMNS + column
				#xbmc.log("Roger, addon here..index: " + str(index), xbmc.LOGINFO)
				if index >= len(self.audiobooks_to_display):
					break

				audiobook = self.audiobooks_to_display[index]
				x_pos = start_x + (COVER_WIDTH + HORIZONTAL_PADDING) * column
				y_pos = start_y + (COVER_HEIGHT + VERTICAL_PADDING) * row

				button_control = xbmcgui.ControlButton(
					x_pos, y_pos, COVER_WIDTH, COVER_HEIGHT, "",
					focusTexture=audiobook['cover_url'],
					noFocusTexture=audiobook['cover_url']
				)
				self.addControl(button_control)
				self.button_controls.append(button_control)

				play_control = xbmcgui.ControlImage(x_pos, y_pos, COVER_WIDTH, COVER_HEIGHT, play_path)
				self.addControl(play_control)
				self.play_controls.append(play_control)
				play_control.setVisible(False)

		button_width = 50
		button_height = 50
		total_width_for_buttons = 2 * button_width + 150
		center_x = (1920 - total_width_for_buttons) // 2

		prev_button_x = center_x
		prev_button_y = (1080 - button_height) - 100
		next_button_x = prev_button_x + button_width + 150
		next_button_y = prev_button_y

		prev_button_image = os.path.join(addon_dir, 'resources', 'skins', 'default', 'media', 'prev.png')
		next_button_image = os.path.join(addon_dir, 'resources', 'skins', 'default', 'media', 'next.png')
		prev_button_image_focus = os.path.join(addon_dir, 'resources', 'skins', 'default', 'media', 'prevb.png')
		next_button_image_focus = os.path.join(addon_dir, 'resources', 'skins', 'default', 'media', 'nextb.png')

		self.prev_button = xbmcgui.ControlButton(
			prev_button_x, prev_button_y, button_width, button_height, "",
			focusTexture=prev_button_image_focus,
			noFocusTexture=prev_button_image
		)
		self.addControl(self.prev_button)

		self.next_button = xbmcgui.ControlButton(
			next_button_x, next_button_y, button_width, button_height, "",
			focusTexture=next_button_image_focus,
			noFocusTexture=next_button_image
		)
		self.addControl(self.next_button)

	def set_audiobook_navigation(self):
		for row in range(MAX_ROWS):
			for column in range(MAX_COLUMNS):
				index = row * MAX_COLUMNS + column
				if index >= len(self.button_controls):
					break

				button = self.button_controls[index]
				above = self.button_controls[index - MAX_COLUMNS] if index - MAX_COLUMNS >= 0 else button

				below = self.button_controls[index + MAX_COLUMNS] if (index + MAX_COLUMNS) < len(self.button_controls) else button
				rows_on_current_page = -(-len(self.audiobooks_to_display) // MAX_COLUMNS)  # Ceiling Division
				if row == rows_on_current_page - 1:  # Wenn es die letzte Zeile auf der aktuellen Seite ist
					below = self.next_button

				if column == 0:
					left = button
				else:
					left = self.button_controls[index - 1]

				# Navigation rechts
				if column == MAX_COLUMNS - 1:
					right = button
				else:
					right = self.button_controls[index + 1]

				button.setNavigation(above, below, left, right)

		self.prev_button.setNavigation(self.button_controls[0], self.prev_button, self.prev_button, self.next_button)
		self.next_button.setNavigation(self.button_controls[0], self.next_button, self.prev_button, self.next_button)

	def onFocus(self, controlId):
		for index, button in enumerate(self.button_controls):
			self.play_controls[index].setVisible(button.getId() == controlId)
			if button.getId() == controlId:
				self.selected_index = index 

	def next_page(self):
		if (self.page + 1) * MAX_PER_PAGE < len(self.audiobooks):
			self.page += 1
			self.selected_index = None
			self.display_audiobooks()		

	def previous_page(self):
		if self.page > 0:
			self.page -= 1
			self.selected_index = None
			self.display_audiobooks()		

	def getRealIndex(self, current_index):
		num_audiobooks = len(self.audiobooks)
		xbmc.log(f"num_audiobooks: {str(num_audiobooks)}", xbmc.LOGINFO)
		xbmc.log(f"self.page: {str(self.page)}", xbmc.LOGINFO)
		current_page = self.page
		real_index = (current_page) * MAX_PER_PAGE + current_index
		return real_index		

	def onAction(self, action):
		if action.getButtonCode() == 216:
			self.close()
		if action.getId() == xbmcgui.ACTION_SELECT_ITEM:
			focus_id = self.getFocusId()
			if focus_id == self.prev_button.getId():  # ID des prev_button
				self.previous_page()
			elif focus_id == self.next_button.getId():  # ID des next_button
				self.next_page()
			else:
				for index, button in enumerate(self.button_controls):
					if focus_id == button.getId():
						xbmc.log(f"index: {index}", xbmc.LOGINFO)
						rindex = self.getRealIndex(index)
						xbmc.log(f"realindex: {rindex}", xbmc.LOGINFO)
						self.show_audiobook_player(rindex)
						break

	def show_audiobook_player(self, index):
		self.selected_index = index
		selected_audiobook = self.audiobooks[index]
		cover = selected_audiobook['cover_url']
		iid = selected_audiobook['id']
		audiobook_data = {
			'id': iid,
			'title': selected_audiobook['title'],
			'cover': cover,
			'description': selected_audiobook['description'],
			'narrator_name': selected_audiobook['narrator_name'],
			'published_year': selected_audiobook['published_year'],
			'publisher': selected_audiobook['publisher'],
			'duration': selected_audiobook['duration'],

		}
			
		dialog = AudioBookPlayer('audiobook_dialog.xml', xbmcaddon.Addon().getAddonInfo('path'), 'default', '1080i', **audiobook_data)
		dialog.doModal()
		del dialog


def select_library(url, token):
	library_service = AudioBookShelfLibraryService(url, token)

	data = library_service.get_all_libraries()
	libraries = data['libraries']
	library_names = [lib['name'] for lib in libraries]

	dialog = xbmcgui.Dialog()
	selected = dialog.select('Wählen Sie eine Bibliothek', library_names)

	if selected != -1:
		selected_library = libraries[selected]
		items = library_service.get_library_items(selected_library['id'])
		audiobooks = []

		for item in items["results"]:
			cover_path = item['media'].get('coverPath', "") or ""
			icon_id = os.path.basename(os.path.dirname(cover_path))
			cover_url = f"{url}/api/items/{icon_id}/cover?token={token}"
			title = item['media']['metadata'].get('title', "") or ""
			description = item['media']['metadata'].get('description', "") or ""
			narrator_name = item['media']['metadata'].get('narratorName', "") or ""
			#xbmc.log("Roger, addon here..item" + str(item), xbmc.LOGINFO)
			publisher = item['media']['metadata'].get('publisher', "") or ""
			published_year = item['media']['metadata'].get('publishedYear', "") or ""
			duration = item['media'].get('duration', 0.0) or 0.0
			iid = item['id']

			audiobook = {
				"id": iid,
				"title": title,
				"cover_url": cover_url,
				"description": description,
				"narrator_name": "Narrator: "+narrator_name,
				"published_year": "Year: "+published_year,
				"publisher": "Publisher: "+publisher,
				"duration": duration,
			}
			audiobooks.append(audiobook)

		return audiobooks


if __name__ == '__main__':
	ip_address = ADDON.getSetting('ipaddress')
	port = ADDON.getSetting('port')
	username = ADDON.getSetting('username')
	password = ADDON.getSetting('password')

	if not ip_address or not port or not username or not password:
		dialog = SettingsDialog()
		dialog.get_and_store_settings()

	url = f"http://{ip_address}:{port}"
	service = AudioBookShelfService(url)

	try:
		server_status = service.server_status()
	except Exception:
		xbmcgui.Dialog().ok('Fehler', 'Audiobookshelf Server ist nicht erreichbar')
		exit()

	try:
		response_data = service.login(username, password)
		token = response_data.get('token')
		#xbmc.log("Roger, addon here..token: " + str(token), xbmc.LOGINFO)
		if not token:
			raise ValueError("Kein Token in der Antwort")
	except Exception:
		xbmcgui.Dialog().ok('Fehler', 'überprüfen Sie Benutzernamen oder Passwort')
		exit()

	audiobooks = select_library(url, token)
	ui = GUI('script-mainwindow.xml', CWD, 'default', '1080i', True, optional1=audiobooks)
	ui.doModal()
	del ui
