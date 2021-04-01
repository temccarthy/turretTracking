import Tkinter as tk
import threading
import win32gui, win32con
import os

import main
import kinectserial as ks

class App(tk.Frame):
	font = "Comic Sans MS"

	def __init__(self, master=None, fullscreen=False):
		tk.Frame.__init__(self, master)
		self.master = master  # master frame
		self.skeleton_list = tk.Listbox(master, height=6, width=20, font=("Comic Sans MS", 16)) # skeleton list

		if fullscreen:
			master.attributes("-fullscreen", True)
		else:
			master.geometry("500x800")

		master.grid_columnconfigure(0, weight=1)

		self.load_main_frame(master)

	def load_main_frame(self, master):
		lbl_title = tk.Label(master=master, text="Voice Activated Gun", bg="red", font=("Comic Sans MS", 24))
		lbl_title.grid(row=0, column=0, sticky="ewn")
		master.grid_rowconfigure(0, weight=0)

		top_btn_row = tk.Frame(master)
		top_btn_row.grid(row=1, column=0)
		master.rowconfigure(1, weight=1)

		reset_btn = self.make_button("Reset Faces", top_btn_row, cmd=main.reset_skeletons_array)
		reset_btn.grid(row=0, column=0, padx=20, pady=20)
		reset_btn = self.make_button("Exit", top_btn_row, cmd=self.quit_app)
		reset_btn.grid(row=0, column=1, padx=20, pady=20)

		mid_btn_row = tk.Frame(master)
		mid_btn_row.grid(row=2, column=0)
		master.rowconfigure(2, weight=1)

		reset_btn = self.make_button("Reload", mid_btn_row, cmd=lambda: self.reloading(reset_btn))
		reset_btn.grid(row=0, column=0, padx=20, pady=20)
		shoot_btn = self.make_button("Shoot", mid_btn_row, cmd=ks.shoot)
		shoot_btn.grid(row=0, column=1, padx=20, pady=20)

		main.skeletons_array.register_callback(self.populate_skeleton_listbox)  # add listener
		self.populate_skeleton_listbox()
		self.skeleton_list.grid(row=3, column=0)
		# master.rowconfigure(2, weight=1)

		feed_row = tk.Frame(master, background="red")
		feed_row.grid(row=4, column=0)
		master.rowconfigure(4, weight=1)

		show_feed_btn = self.make_button("Hide Feed", feed_row, cmd=lambda: self.flip_show_video(show_feed_btn))
		show_feed_btn.grid(row=0, column=0)

	def make_button(self, text, master, cmd=None):
		btn = tk.Button(text=text, master=master, padx=10, pady=10, bg="sky blue", font=('Comic Sans MS', 16), command=cmd)
		return btn

	def flip_show_video(self, btn):
		# showing and hiding window here
		main.argDict["show_video"] = not main.argDict["show_video"]
		video = win32gui.FindWindow(None, "KINECT Video Stream")
		if main.argDict["show_video"]:
			win32gui.ShowWindow(video, win32con.SW_SHOWDEFAULT)
			btn["text"] = "Hide Feed"
		else:
			win32gui.ShowWindow(video, win32con.SW_MINIMIZE)
			btn["text"] = "Show Feed"

	def reloading(self, btn):
		if btn["text"] == "Reload":
			ks.reload_mag()
			btn["text"] = "Finish Reload"
		else:
			ks.finish_reload()
			btn["text"] = "Reload"


	# relies on observable list being updated and sending call to this function
	def populate_skeleton_listbox(self):
		self.skeleton_list.delete(0, tk.END)
		for index,skele in enumerate(main.skeletons_array.value):
			line = "Skeleton " + str(index+1)
			if skele.present:
				line += str(" - " + skele.name)
			else:
				line += str(" - empty")
			self.skeleton_list.insert(tk.END, line)

	def quit_app(self):
		os._exit(1)


if __name__ == "__main__":
	root = tk.Tk()
	app = App(root, fullscreen=False)
	thread1 = threading.Thread(target=main.main_loop, args=[main.argDict])
	thread1.start()
	root.mainloop()
