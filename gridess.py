import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "students.db"

# -------------------------
#   DATABASE
# -------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            note TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_student(name: str, age: str, note: str):
    if not name.strip():
        raise ValueError("Name is required")

    try:
        age_val = int(age) if age.strip() else None
    except ValueError:
        raise ValueError("Age must be a number")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO students (name, age, note, created_at) VALUES (?, ?, ?, ?)",
        (name.strip(), age_val, note.strip(), datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()


def load_students():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, name, age, note, created_at FROM students ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return rows

# -------------------------
#   GUI
# -------------------------
def build_gui():
    root = tk.Tk()
    root.title("Students")
    root.geometry("550x500")
    root.configure(bg="#0f1e0f")  # dark green-black

    style = ttk.Style()
    style.theme_use("clam")

    # COLORS
    main_bg = "#0f1e0f"      # very dark green
    entry_bg = "#1d3520"
    text_bg = "#1e3a22"
    text_fg = "white"
    button_bg = "#28a745"   # green button
    button_active = "#1f7f36"

    # Label style
    style.configure("TLabel", background=main_bg, foreground="white", font=("Segoe UI", 11))
    style.configure("TFrame", background=main_bg)

    # Entry style
    style.configure("TEntry",
                    fieldbackground=entry_bg,
                    background=entry_bg,
                    foreground="white",
                    bordercolor="#3b6e47")

    # Button style
    style.configure("TButton",
                    background=button_bg,
                    foreground="white",
                    font=("Segoe UI", 11, "bold"),
                    padding=6)
    style.map("TButton",
              background=[("active", button_active)])

    frm = ttk.Frame(root, padding=10)
    frm.pack(fill="both", expand=True)

    # INPUTS
    ttk.Label(frm, text="Name:").grid(row=0, column=0, sticky="w", pady=3)
    name_entry = ttk.Entry(frm, width=35)
    name_entry.grid(row=0, column=1, sticky="w")

    ttk.Label(frm, text="Age:").grid(row=1, column=0, sticky="w", pady=3)
    age_entry = ttk.Entry(frm, width=10)
    age_entry.grid(row=1, column=1, sticky="w")

    ttk.Label(frm, text="Note:").grid(row=2, column=0, sticky="nw", pady=3)

    note_text = tk.Text(frm, width=35, height=5,
                        bg=text_bg, fg="white", insertbackground="white",
                        highlightbackground="#3b6e47", highlightcolor="#3b6e47")
    note_text.grid(row=2, column=1, sticky="w")

    # Students list
    ttk.Label(frm, text="Students:", font=("Segoe UI", 12, "bold")).grid(row=4, column=0, columnspan=2, pady=10)

    students_box = tk.Text(frm, width=60, height=12,
                           bg=text_bg, fg="white",
                           state="disabled", insertbackground="white",
                           highlightbackground="#3b6e47", highlightcolor="#3b6e47")
    students_box.grid(row=5, column=0, columnspan=2, pady=5)

    # REFRESH
    def refresh_students_label():
        rows = load_students()
        students_box.config(state="normal")
        students_box.delete("1.0", "end")

        if not rows:
            students_box.insert("end", "Nuk ka regjistrime.")
        else:
            for r in rows:
                id_, name, age, note, created = r
                age_str = str(age) if age is not None else "-"
                short_note = (note[:60] + "...") if note and len(note) > 60 else (note or "")
                students_box.insert("end", f"{id_}: {name} | age: {age_str} | {short_note}\n")

        students_box.config(state="disabled")

    # SAVE BUTTON
    save_btn = ttk.Button(frm, text="Save", command=lambda: on_save())
    save_btn.grid(row=3, column=1, sticky="e", pady=6)

    def on_save():
        try:
            save_student(name_entry.get(), age_entry.get(), note_text.get("1.0", "end"))
            name_entry.delete(0, "end")
            age_entry.delete(0, "end")
            note_text.delete("1.0", "end")
            refresh_students_label()
            messagebox.showinfo("Saved", "Regjistrimi u ruajt me sukses.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    refresh_students_label()
    return root


if __name__ == "__main__":
    init_db()
    app = build_gui()
    app.mainloop()
