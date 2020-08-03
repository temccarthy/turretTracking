import Tkinter as tk
import threading

import main


class App(tk.Frame):
	font = "Comic Sans MS"

	def __init__(self, master=None, fullscreen=False):
		tk.Frame.__init__(self, master)
		self.master = master  # master frame

		if fullscreen:
			master.attributes("-fullscreen", True)
		else:
			master.geometry("500x800")

		master.grid_columnconfigure(0, weight=1)

		# ttk.Style().theme_use('clam')
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

		log_btn = self.make_button("Logs", top_btn_row)
		log_btn.grid(row=1, column=0, padx=20, pady=20)
		screen_btn = self.make_button("Darken Screen", top_btn_row)
		screen_btn.grid(row=1, column=1, padx=20, pady=20)

		feed_row = tk.Frame(master, background="red")
		feed_row.grid(row=2, column=0)
		master.rowconfigure(2, weight=1)

		show_feed_btn = self.make_button("Show Feed", feed_row, cmd=self.flip_show_video)
		show_feed_btn.grid(row=0, column=0)
		feed_open_lbl = tk.Label(master=feed_row, text="somthing reallllllllllly long", bg="white", font=("Comic Sans MS", 16))
		feed_open_lbl.grid(row=1, column=0)

	def make_button(self, text, master, cmd=None):
		btn = tk.Button(text=text, master=master, padx=10, pady=10, bg="sky blue", font=('Comic Sans MS', 16), command=cmd)
		return btn

	def flip_show_video(self):
		# showing and hiding window here
		main.argDict["show_video"] = not main.argDict["show_video"]



if __name__ == "__main__":
	root = tk.Tk()
	app = App(root)
	thread1 = threading.Thread(target=main.main_loop, args=[main.argDict])
	thread1.start()
	root.mainloop()
	# main.main_loop(show_video=True)
