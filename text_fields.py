import tkinter as tk


class TextField(tk.Frame):
    def __init__(self, parent, label='', passwordField=False, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.configure(bg=parent['bg'])

        self.text_entry = tk.StringVar()

        self.title = tk.Label(self, text=label, width=20, bg=parent['bg'], fg="white", anchor="w")
        self.title.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)

        if passwordField:
            self.field = tk.Entry(self, width=30, textvariable=self.text_entry, show="*", bg="#2a2a2a", fg="white",
                                  insertbackground="white", relief="flat")
        else:
            self.field = tk.Entry(self, width=30, textvariable=self.text_entry, bg="#2a2a2a", fg="white",
                                  insertbackground="white", relief="flat")

        self.field.grid(row=0, column=1, padx=10, pady=5)

    def reset(self):
        self.text_entry.set("")

    def get(self):
        return self.text_entry.get()
