import os
import sys
import json
import platform
import subprocess as sub
from tkinter import *
from tkinter import filedialog as fd
from tkinter.messagebox import showerror
from tkinter.messagebox import showinfo

# Ensure that settings.json is in the correct location
try:
  with open("settings.json", "r") as f:
    settings = json.load(f)
except FileNotFoundError:
  showerror(title="SwiftWrite: Error 001", message="'settings.json' file not found.")
  sys.exit()
except json.JSONDecodeError:
  showerror(title="SwiftWrite: Error 002", message="Could not decode 'settings.json'. Ensure it contains valid JSON.")
  sys.exit()

def print_document():
  # Function to print the document
  system = platform.system()
  content = text.get("1.0", END)
  if content.strip():
    # Save the content to a temporary file
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding='utf-8') as temp_file:
      temp_file.write(content)
      temp_filepath = temp_file.name
    try:
      if system == "Windows":
        os.startfile(temp_filepath, "print")
      elif system == "Linux" or system == "Darwin" or system == "FreeBSD" or system == "OpenBSD":
        sub.run(["lp", temp_filepath])
      else:
        showerror(title="SwiftWrite: Error 003", message="Unknown operating system")
    except Exception as e:
      showerror(title="SwiftWrite: Error 004", message=f"An error occurred while printing: {e}")
  else:
    showinfo(title="SwiftWrite: Error 005", message="Nothing to print.")

def read_file():
  # Function to open a file and display its contents
  filepath = fd.askopenfilename()
  if filepath:
    try:
      with open(filepath, "r", encoding='utf-8') as f:
        content = f.read()
      text.delete("1.0", END)
      text.insert("1.0", content)
      return filepath
    except Exception as e:
      showerror("SwiftWrite: Error 006", f"An error occurred while opening the file: {e}")

def save_as():
  # Function to save the current text to a file
  filepath = fd.asksaveasfilename(defaultextension=".txt")
  if filepath:
    try:
      with open(filepath, 'w', encoding='utf-8') as f:
        f.write(text.get("1.0", END))
    except Exception as e:
      showerror("SwiftWrite: Error 007", f"An error occurred while saving the file: {e}")

def find_text():
  # Create a new Toplevel window for search
  find_window = Toplevel(r)
  find_window.title("SwiftWrite: Find")
  find_window.transient(r)
  find_window.resizable(False, False)
  
  # Variables
  search_var = StringVar()
  search_var.trace('w', lambda *args: reset_search())
  
  # Label and input field for the search query
  Label(find_window, text="Find:").grid(row=0, column=0, padx=5, pady=5)
  search_entry = Entry(find_window, textvariable=search_var, width=30)
  search_entry.grid(row=0, column=1, padx=5, pady=5, columnspan=2)
  search_entry.focus_set()
  
  # Buttons "Find Next", "Find Previous", and "Close"
  Button(find_window, text="Find Next", command=lambda: search_action('next')).grid(row=1, column=0, padx=5, pady=5)
  Button(find_window, text="Find Previous", command=lambda: search_action('prev')).grid(row=1, column=1, padx=5, pady=5)
  Button(find_window, text="Close", command=lambda: close_search(find_window)).grid(row=1, column=2, padx=5, pady=5)
  
  # Initialize variables
  search_indices = []
  current_index = -1
  
  def reset_search():
    # Clear highlights when the search query changes
    nonlocal search_indices, current_index
    text.tag_remove('highlight', '1.0', END)
    text.tag_remove('current_highlight', '1.0', END)
    search_indices = []
    current_index = -1
  
  def search_action(direction):
    nonlocal search_indices, current_index
    term = search_var.get()
    if not term:
      showinfo("SwiftWrite: Search", "Please enter a search term.")
    if not search_indices:
      # First search, find all matches
      start_pos = '1.0'
      while True:
        start_pos = text.search(term, start_pos, nocase=1, stopindex=END)
        if not start_pos:
          break
        end_pos = f"{start_pos}+{len(term)}c"
        text.tag_add('highlight', start_pos, end_pos)
        search_indices.append(start_pos)
        start_pos = end_pos
      text.tag_config('highlight', background='yellow')
      if not search_indices:
        showinfo("SwiftWrite: Search", "No matches found.")
    # Navigate through matches
    if direction == 'next':
      current_index = (current_index + 1) % len(search_indices)
    elif direction == 'prev':
      current_index = (current_index - 1) % len(search_indices)
    highlight_current()
  
  def highlight_current():
    nonlocal search_indices, current_index
    # Scroll to the current match
    text.tag_remove('current_highlight', '1.0', END)
    idx = search_indices[current_index]
    end_idx = f"{idx}+{len(search_var.get())}c"
    text.tag_add('current_highlight', idx, end_idx)
    text.tag_config('current_highlight', background='orange')
    text.see(idx)
  
  # Bind the Enter key to the "Find Next" action
  find_window.bind('<Return>', lambda event: search_action('next'))
  find_window.protocol("WM_DELETE_WINDOW", lambda: close_search(find_window))
  
  def close_search(window):
    # Clear highlights when closing the search window
    text.tag_remove('highlight', '1.0', END)
    text.tag_remove('current_highlight', '1.0', END)
    window.destroy()

# Create the main application window
r = Tk()
r.title("SwiftWrite")

# Create a frame for the Text widget and Scrollbar
text_frame = Frame(r)
text_frame.pack(fill=BOTH, expand=1)

# Add vertical Scrollbar to the Text widget
scrollbar = Scrollbar(text_frame)
scrollbar.pack(side=RIGHT, fill=Y)

# Create the Text widget with Scrollbar configuration
text = Text(text_frame, font=settings.get("font", ("Arial", 12)), yscrollcommand=scrollbar.set, wrap=NONE, undo=True)
text.pack(fill=BOTH, expand=1)

# Configure Scrollbar command
scrollbar.config(command=text.yview)

# Create the menu
menu = Menu(r)

# File menu
file_menu = Menu(menu, tearoff=0)
file_menu.add_command(label="Open", command=read_file)
file_menu.add_command(label="Save as...", command=save_as)
file_menu.add_command(label="Print", command=print_document)
menu.add_cascade(label="File", menu=file_menu)

# Edit menu
edit_menu = Menu(menu, tearoff=0)
edit_menu.add_command(label="Find", command=find_text)
menu.add_cascade(label="Edit", menu=edit_menu)

# Configure the menu
r.config(menu=menu)

# Start the main event loop
r.mainloop()
