import tkinter as tk
from tkinter import filedialog, messagebox, Menu, simpledialog
from pygments import lex
from pygments.lexers import get_lexer_by_name
from pygments.token import Token
from pygments.styles import get_style_by_name

class GuiVim:
    def __init__(self, root):
        self.root = root
        self.root.title("GuiVim")
        self.root.geometry("800x600")
        self.root.configure(bg="#1e1e1e")

        self.menu = Menu(self.root)
        self.root.config(menu=self.menu)

        self.file_menu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Open", command=self.open_file)
        self.file_menu.add_command(label="Save", command=self.save_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)

        self.text = tk.Text(self.root, bg="#1e1e1e", fg="#d4d4d4", insertbackground="white",
                            wrap="none", font=("Consolas", 12), padx=10, pady=10)
        self.text.pack(fill=tk.BOTH, expand=1)

        self.scrollbar_y = tk.Scrollbar(self.text)
        self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrollbar_x = tk.Scrollbar(self.text, orient=tk.HORIZONTAL)
        self.scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.text.config(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)
        self.scrollbar_y.config(command=self.text.yview)
        self.scrollbar_x.config(command=self.text.xview)

        self.mode = "normal"
        self.status_bar = tk.Label(self.root, text="", bg="#1e1e1e", fg="#d4d4d4", anchor="w")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.text.bind("<Key>", self.handle_key)
        self.text.bind("<Escape>", self.switch_to_normal_mode)
        self.text.bind("<Control-h>", self.show_language_dialog)

        self.command_buffer = ""
        self.language = "python"
        self.highlight_syntax()

    def handle_key(self, event):
        if self.mode == "normal":
            self.handle_normal_mode(event)
        elif self.mode == "insert":
            self.handle_insert_mode(event)
        elif self.mode == "command":
            self.handle_command_mode(event)

    def handle_normal_mode(self, event):
        key = event.keysym
        if key == "i":
            self.switch_to_insert_mode()
        elif key == ":":
            self.switch_to_command_mode()
        elif key == "h":
            self.move_cursor(-1, 0)
        elif key == "j":
            self.move_cursor(0, 1)
        elif key == "k":
            self.move_cursor(0, -1)
        elif key == "l":
            self.move_cursor(1, 0)

    def handle_insert_mode(self, event):
        pass

    def handle_command_mode(self, event):
        key = event.char
        if key == "\r":
            self.execute_command()
        elif key == "\x08":
            self.command_buffer = self.command_buffer[:-1]
        elif key:
            self.command_buffer += key
        self.status_bar.config(text=f"COMMAND MODE: {self.command_buffer}")

    def switch_to_normal_mode(self, event=None):
        self.mode = "normal"
        self.text.config(insertwidth=2)
        self.status_bar.config(text="")

    def switch_to_insert_mode(self):
        self.mode = "insert"
        self.text.config(insertwidth=4)
        self.status_bar.config(text="")

    def switch_to_command_mode(self):
        self.mode = "command"
        self.command_buffer = ""
        self.status_bar.config(text="COMMAND MODE: ")

    def execute_command(self):
        command = self.command_buffer.strip()
        if command == "w":
            self.save_file()
        elif command == "q":
            self.root.quit()
        elif command == "wq":
            self.save_file()
            self.root.quit()
        elif command.startswith("setlang "):
            self.set_language(command.split(" ")[1])
        else:
            messagebox.showerror("Error", f"Unknown command: {command}")
        self.switch_to_normal_mode()

    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("All Files", "*.*")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(self.text.get(1.0, tk.END))

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("All Files", "*.*")])
        if file_path:
            with open(file_path, "r") as file:
                self.text.delete(1.0, tk.END)
                self.text.insert(tk.END, file.read())
            self.highlight_syntax()

    def move_cursor(self, x, y):
        cursor_pos = self.text.index(tk.INSERT)
        line, col = map(int, cursor_pos.split("."))
        new_line, new_col = line + y, col + x
        self.text.mark_set(tk.INSERT, f"{new_line}.{new_col}")
        self.text.see(tk.INSERT)

    def set_language(self, language):
        self.language = language
        self.highlight_syntax()
        self.status_bar.config(text=f"Language set to: {language.upper()}")

    def highlight_syntax(self):
        self.text.mark_set("range_start", "1.0")
        try:
            lexer = get_lexer_by_name(self.language)
            style = get_style_by_name("monokai")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load lexer for {self.language}: {e}")
            return

        self.text.tag_remove("Token", "1.0", tk.END)

        for token, content in lex(self.text.get(1.0, tk.END), lexer):
            self.text.mark_set("range_end", "range_start + %dc" % len(content))
            tag_name = str(token)
            self.text.tag_add(tag_name, "range_start", "range_end")

            token_style = style.style_for_token(token)
            if 'color' in token_style:
                color = token_style['color']
                tk_color = color if color.startswith("#") else f"#{color}"
            else:
                tk_color = "#d4d4d4"

            self.text.tag_config(tag_name, foreground=tk_color)
            self.text.mark_set("range_start", "range_end")

    def show_language_dialog(self, event=None):
        languages = ["python", "javascript", "java", "c", "cpp", "fortran", "go", "bash"]
        language = simpledialog.askstring("Select Language", "Enter language:", initialvalue=self.language,
                                          parent=self.root)
        if language and language.lower() in languages:
            self.set_language(language.lower())
            messagebox.showinfo("Language Hint", f"Language set to {language.upper()}. "
                                                 f"Use :setlang <language> to change it.")
        else:
            messagebox.showerror("Error", "Invalid language selected.")

if __name__ == "__main__":
    root = tk.Tk()
    editor = GuiVim(root)
    root.mainloop()
