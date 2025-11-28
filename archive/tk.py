import tkinter as tk

print(tk.Tk().tk.call("info", "patchlevel"))

# Create the main window
root = tk.Tk()
root.title("My App")
root.geometry("400x300")

# Add widgets here
label = tk.Label(root, text="Hello, Tkinter!")
label.pack(pady=20)

# Run the app
root.mainloop()