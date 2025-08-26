import tkinter as tk
import requests
import json

URL = "http://127.0.0.1:8000/assistant/text-command"

def send_request(event=None):
    text = entry.get()
    headers = {
        "Content-Type": "application/json",
        "x-auth": "AUTH_TOKEN_SECRET_TO_REPLACE"
    }
    try:
        response = requests.post(URL, json={"message": text}, headers=headers)
        response.raise_for_status()
        try:
            json_response = response.json()
            output_text = json.dumps(json_response, indent=4, ensure_ascii=False)
        except json.JSONDecodeError:
            output_text = response.text
    except requests.exceptions.RequestException as e:
        output_text = f"Błąd: {e}"

    for widget in root.winfo_children():
        widget.destroy()

    output_label = tk.Label(root, text=output_text, wraplength=800, justify="left")
    output_label.pack(padx=10, pady=10)

    close_button = tk.Button(root, text="Zamknij", command=root.destroy)
    close_button.pack(pady=5)
    close_button.focus()

    root.bind('<Return>', lambda e: root.destroy())

root = tk.Tk()
root.title("Komenda dla asystenta")

entry = tk.Entry(root, width=120)
entry.pack(padx=10, pady=10)
entry.bind('<Return>', send_request)

button = tk.Button(root, text="Wyślij", command=send_request)
button.pack(pady=5)

entry.focus()
root.mainloop()
