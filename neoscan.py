import customtkinter as ctk
import socket, threading, queue, time

# Ways to take this:
# - Make it much faster (it's very slow)
# - Display what use case the open port is probably being used for
# - Play a working sound when it's working and a satisfying ding when an open port is found


def scan():
    ip = ip_entry.get()
    port_range = port_entry.get()

    # Validation
    if ip == '':
        ip_entry.configure(placeholder_text_color="red")
        raise ValueError("Enter an ip address")

    try:
        socket.inet_aton(socket.gethostbyname(ip))
    except socket.error:
        ip_entry.configure(text_color="red")
        raise ValueError("Invalid IP address")

    ip_entry.configure(placeholder_text_color="white")
    ip_entry.configure(text_color="white")
        
    if port_range == '':
        port_entry.configure(placeholder_text_color="red")
        raise ValueError("Enter an port range")
    
    if '-' not in port_range:
        port_entry.configure(text_color="red")
        raise ValueError("Port range must contain a hyphen (e.g. 20-80)")
    
    port_range_parts = port_range.split('-')
    if len(port_range_parts) != 2:
        port_entry.configure(text_color="red")
        raise ValueError("Port range must be two numbers separated by a single hyphen")
    
    start_port, end_port = port_range_parts
    if not (start_port.isdigit() and end_port.isdigit()):
        port_entry.configure(text_color="red")
        raise ValueError("Both start and end of port range must be valid integers")
    start_port = int(start_port); end_port = int(end_port)

    if start_port >= end_port:
        port_entry.configure(text_color="red")
        raise ValueError("Start port must be lower than end port")

    port_entry.configure(placeholder_text_color="white")
    port_entry.configure(text_color="white")

    # Hardcoded values only for debugging
    # ip = socket.gethostbyname("google.com")
    # print(f"Resolved to: {ip}")
    # start_port, end_port = [441, 500]
    # port_range = f"{start_port}-{end_port}"

    log(">>> NEOSCAN ENGAGED <<<", "start")
    log(f"Target: {socket.gethostbyname(ip)} | Range: {port_range}", "info")
    log("-" * 50, "info")
    
    # Disable button during scan
    update_queue.put(('button', "disabled"))

    def start_thread():
        open = 0; closed = 0;
        total_scan_time = 0

        for port in range(start_port, end_port+1):
            avg_scan_time = total_scan_time / (open + closed) if total_scan_time > 0 else 0
            print(avg_scan_time)

            update_queue.put(('progress', f"Scanning port {port}... {avg_scan_time:.2f}s/port"))
            start_time = time.perf_counter()

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            try:
                result = sock.connect_ex((ip, port))
            except socket.error:
                result = 1
                
            # print(f"Port {port}: raw result = {result}")
            sock.close()

            scan_duration = time.perf_counter() - start_time
            total_scan_time += scan_duration

            if result == 0:
                open += 1
                update_queue.put(('log', f"Port {port:5} → OPEN", "open"))
            else:
                closed += 1

        update_queue.put(('log', "-" * 50, "info"))
        update_queue.put(('log', f"Scan complete → {open} open, {closed} closed/filtered\n", "open"))
        update_queue.put(('progress', f"Scan complete. {total_scan_time:.2f} total."))
        update_queue.put(('button', "normal"))

    threading.Thread(target=start_thread, daemon=True).start()


def poll_updates():
    while not update_queue.empty():
        task = update_queue.get()
        if task[0] == 'log':
            log(task[1], task[2])
        elif task[0] == 'progress':
            progress_label.configure(text=task[1])
        elif task[0] == 'button':
            scan_button.configure(state=task[1])
    app.after(100, poll_updates)


def log(message: str, tag="info"):
    log_text.configure(state="normal")
    log_text.insert("end", message + "\n", tag)
    log_text.see("end")  # auto-scroll
    log_text.configure(state="disabled")
    app.update_idletasks()  # forces GUI to refresh immediately


ctk.set_appearance_mode("dark")     # or "light" or "system"
ctk.set_default_color_theme("dark-blue")  # try "green" later, it's sick

app = ctk.CTk()
app.geometry("600x700")
app.title("NeoScan v0.01")

# Big hacker-looking title
title = ctk.CTkLabel(app, text="NEOSCAN", font=("Courier", 48, "bold"), text_color="#00ff41")
title.pack(pady=30)

# Input row
frame = ctk.CTkFrame(app)
frame.pack(pady=20, padx=40, fill="x")

ctk.CTkLabel(frame, text="Target:", font=("Courier", 16)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
ip_entry = ctk.CTkEntry(frame, width=300, placeholder_text="ip address")
ip_entry.grid(row=0, column=1, padx=10, pady=10)

ctk.CTkLabel(frame, text="Port Range:", font=("Courier", 16)).grid(row=1, column=0, padx=10, pady=10, sticky="w")
port_entry = ctk.CTkEntry(frame, width=200, placeholder_text="i.e. 1337-13337")
port_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")

# Scan button that looks dangerous
scan_button = ctk.CTkButton(app, text="ENGAGE", width=200, height=50,
                            font=("Courier", 20, "bold"),
                            fg_color="#00ff41", hover_color="#00cc33",
                            text_color="black", cursor="circle", command=scan)
scan_button.pack(pady=30)

# New Live Log Code
# ─── Live log + results area ─────────────────────────────────────
log_frame = ctk.CTkFrame(app)
log_frame.pack(pady=20, padx=40, fill="both", expand=True)

# Live scanning log (the Matrix rain part)
log_text = ctk.CTkTextbox(log_frame, height=200, font=("Courier", 14))
log_text.pack(fill="both", expand=True)

# Make it read-only + green-on-black hacker style
log_text.configure(state="disabled")
log_text.tag_config("start", foreground="#ffe34d")
log_text.tag_config("open", foreground="#00ff41")
log_text.tag_config("closed", foreground="#ff3333")
log_text.tag_config("info", foreground="#33ccff")

# Optional: progress label
progress_label = ctk.CTkLabel(app, text="Ready.", font=("Courier", 16))
progress_label.pack(pady=5)

update_queue = queue.Queue()
poll_updates()

app.mainloop()