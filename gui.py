import Tkinter as tk
import ttk
# import main


class App(tk.Frame):
    def __init__(self, master=None, fullscreen=False):
        tk.Frame.__init__(self, master)
        self.master = master  # master frame

        if fullscreen:
            master.attributes("-fullscreen", True)
        else:
            root.geometry("500x800")

        # ttk.Style().theme_use('clam')
        self.load_main_frame(master)

    def load_main_frame(self, master):
        frm_title = tk.Frame(master=master, borderwidth=1)
        frm_title.grid(row=0, column=0)

        lbl_title = tk.Label(text="Voice Activated Gun",
                             bg="red",
                             font=("Comic Sans MS", 24))
        lbl_title.pack(fill='x')

        frm_body = tk.Frame(master=master)
        frm_body.grid(row=1, column=0)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
