
import os, json, tkinter as tk
from tkinter import ttk, messagebox
from ai_client.client import AIClient
from ai_client.ai_request import AIRequest
from ai_client.recipe_schema import schema_description
from ai_client.supported_models import get_supported_models
from ai_client.storage import get_store

class App:
    def __init__(self, root):
        self.__root = root
        self.__root.title("Recipe JSON Generator")
        self.__provider_var = tk.StringVar(value="mock")
        self.__model_var = tk.StringVar(value="mock-1")
        self.__prompt_var = tk.StringVar(value="Generate a spiced gram flour snack recipe")
        self.__build_ui()
        self.__refresh_models()

    def __build_ui(self):
        frm = ttk.Frame(self.__root, padding=12)
        frm.grid(row=0, column=0, sticky="nsew")
        self.__root.columnconfigure(0, weight=1)
        self.__root.rowconfigure(0, weight=1)

        menubar = tk.Menu(self.__root)
        provider_menu = tk.Menu(menubar, tearoff=0)
        provider_menu.add_command(label="Mock", command=lambda: self.__set_provider_model("mock", "mock-1"))
        provider_menu.add_command(label="OpenAI", command=lambda: self.__set_provider_model("openai", None))
        menubar.add_cascade(label="Provider", menu=provider_menu)
        self.__root.config(menu=menubar)

        row = 0
        ttk.Label(frm, text="Provider:").grid(row=row, column=0, sticky="w")
        self.__provider_cb = ttk.Combobox(frm, textvariable=self.__provider_var, values=["mock","openai"], state="readonly", width=10)
        self.__provider_cb.grid(row=row, column=1, sticky="w")
        self.__provider_cb.bind("<<ComboboxSelected>>", self.__on_provider_selected)

        ttk.Label(frm, text="Model:").grid(row=row, column=2, sticky="w", padx=(12,0))
        self.__model_cb = ttk.Combobox(frm, textvariable=self.__model_var, values=[], state="readonly", width=24)
        self.__model_cb.grid(row=row, column=3, sticky="we")
        frm.columnconfigure(3, weight=1)

        row += 1
        ttk.Label(frm, text="Prompt:").grid(row=row, column=0, sticky="nw", pady=(12,0))
        self.__prompt_entry = tk.Text(frm, height=4, wrap="word")
        self.__prompt_entry.insert("1.0", self.__prompt_var.get())
        self.__prompt_entry.grid(row=row, column=1, columnspan=3, sticky="nsew", pady=(12,0))
        frm.rowconfigure(row, weight=1)

        row += 1
        self.__generate_btn = ttk.Button(frm, text="Generate JSON", command=self.__on_generate)
        self.__generate_btn.grid(row=row, column=3, sticky="e", pady=12)

        # Storage buttons
        row += 1
        store_bar = ttk.Frame(frm)
        store_bar.grid(row=row, column=0, columnspan=4, sticky="we")
        ttk.Button(store_bar, text="Save to DB", command=self.__on_save).pack(side="left")
        ttk.Button(store_bar, text="Browse DB", command=self.__on_browse).pack(side="left")
        ttk.Button(store_bar, text="View Recipe", command=self.__on_view).pack(side="left")

        row += 1
        ttk.Label(frm, text="Output (JSON):").grid(row=row, column=0, sticky="w")
        row += 1
        self.__output = tk.Text(frm, height=18, wrap="none")
        self.__output.grid(row=row, column=0, columnspan=4, sticky="nsew")
        frm.rowconfigure(row, weight=2)

        row += 1
        ttk.Label(frm, text="Schema (for reference):").grid(row=row, column=0, sticky="w", pady=(12,0))
        row += 1
        self.__schema_box = tk.Text(frm, height=8, wrap="none")
        self.__schema_box.grid(row=row, column=0, columnspan=4, sticky="nsew")
        self.__schema_box.insert("1.0", json.dumps(schema_description(), indent=2))
        self.__schema_box.configure(state="disabled")

    def __refresh_models(self):
        provider = self.__provider_var.get()
        models = get_supported_models(provider)
        self.__model_cb['values'] = models
        if self.__model_var.get() not in models:
            self.__model_var.set(models[0] if models else "")

    def __on_provider_selected(self, event=None):
        self.__refresh_models()

    def __set_provider_model(self, provider, model):
        self.__provider_var.set(provider)
        self.__refresh_models()
        if model is not None:
            models = get_supported_models(provider)
            self.__model_var.set(model if model in models else (models[0] if models else ""))

    def __on_generate(self):
        provider = self.__provider_var.get()
        model = self.__model_var.get().strip()
        prompt = self.__prompt_entry.get("1.0", "end").strip()
        if not model:
            messagebox.showerror("Error", "Model cannot be empty")
            return
        if not prompt:
            messagebox.showerror("Error", "Prompt cannot be empty")
            return
        try:
            client = AIClient(provider=provider, model=model)
            system = "Return ONLY valid JSON matching the provided schema. No prose. Use the exact keys from schema."
            req = AIRequest(model=model, system=system, user=prompt, temperature=0.2, max_tokens=800)
            res = client.generate(req)
            parsed = json.loads(res.text)
            self.__output.delete("1.0", "end")
            self.__output.insert("1.0", json.dumps(parsed, indent=2))
        except Exception as e:
            self.__output.delete("1.0", "end")
            self.__output.insert("1.0", f"Error: {e}")

    def __on_save(self):
        try:
            text = self.__output.get("1.0", "end").strip()
            if not text:
                messagebox.showwarning("Nothing to save", "Output is empty. Generate a recipe first.")
                return
            data = json.loads(text)
        except Exception as e:
            messagebox.showerror("Invalid JSON", f"Could not parse JSON from output box:\n{e}")
            return
        try:
            store = get_store()
            rid = store.save(data, user_id=None)
            messagebox.showinfo("Saved", f"Recipe saved with ID: {rid}")
        except Exception as e:
            messagebox.showerror("DB Error", f"Failed to save recipe:\n{e}")

    def __on_browse(self):
        store = get_store()
        try:
            rows = store.list(limit=200)
        except Exception as e:
            messagebox.showerror("DB Error", f"Failed to list recipes:\n{e}")
            return
        win = tk.Toplevel(self.__root)
        win.title("Recipes in Database")
        win.geometry("700x400")
        top = ttk.Frame(win, padding=8); top.pack(fill="x")
        tk.Label(top, text="Search:").pack(side="left")
        search_var = tk.StringVar()
        search_entry = ttk.Entry(top, textvariable=search_var, width=30)
        search_entry.pack(side="left", padx=6)
        list_frame = ttk.Frame(win, padding=8); list_frame.pack(fill="both", expand=True)
        cols = ("id", "title", "created_at")
        tree = ttk.Treeview(list_frame, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=200 if c != "title" else 350, anchor="w")
        tree.pack(fill="both", expand=True)
        def refresh(items):
            for i in tree.get_children():
                tree.delete(i)
            for r in items:
                tree.insert("", "end", values=(r.get("id"), r.get("title"), r.get("created_at")))
        refresh(rows)

        def do_search(*args):
            q = search_var.get().strip()
            try:
                items = store.search(q, limit=200) if q else store.list(limit=200)
                refresh(items)
            except Exception as e:
                messagebox.showerror("DB Error", f"Search failed:\n{e}")
        search_var.trace_add("write", lambda *_: do_search())

        btns = ttk.Frame(win, padding=8); btns.pack(fill="x")
        def load_selected():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Select", "Select a row first.")
                return
            rid = tree.item(sel[0])["values"][0]
            row = store.get(rid)
            if not row:
                messagebox.showerror("Not found", "Recipe not found.")
                return
            try:
                data = json.loads(row["json"])
                self.__output.delete("1.0", "end")
                self.__output.insert("1.0", json.dumps(data, indent=2))
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Could not load recipe JSON:\n{e}")
        ttk.Button(btns, text="Load", command=load_selected).pack(side="left")
        def delete_selected():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Select", "Select a row first.")
                return
            rid = tree.item(sel[0])["values"][0]
            import tkinter.messagebox as mbox
            if not mbox.askyesno("Confirm", "Delete this recipe?"):
                return
            ok = store.delete(rid)
            if ok:
                do_search()
            else:
                messagebox.showerror("Error", "Delete failed.")
        ttk.Button(btns, text="Delete", command=delete_selected).pack(side="left")


    def __on_view(self):
        # Parse JSON from output box and render a child window
        try:
            text = self.__output.get("1.0", "end").strip()
            if not text:
                from tkinter import messagebox
                messagebox.showwarning("Nothing to view", "Output is empty. Generate or load a recipe first.")
                return
            data = json.loads(text)
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Invalid JSON", f"Could not parse JSON from output box:\n{e}")
            return
        self.__open_view_window(data)

    def __open_view_window(self, data: dict):
        import tkinter as tk
        from tkinter import ttk

        win = tk.Toplevel(self.__root)
        title = data.get("title") or "Recipe"
        win.title(f"View: {title}")
        win.geometry("800x600")

        # Scrollable frame pattern (Canvas + Frame + Scrollbar)
        container = ttk.Frame(win); container.pack(fill="both", expand=True)
        canvas = tk.Canvas(container, highlightthickness=0)
        vsb = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        content = ttk.Frame(canvas)
        content_id = canvas.create_window((0,0), window=content, anchor="nw")

        def on_configure(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfigure(content_id, width=canvas.winfo_width())
        content.bind("<Configure>", on_configure)
        win.bind("<Configure>", on_configure)

        # Helpers
        def add_section(header: str):
            lbl = ttk.Label(content, text=header, font=("Segoe UI", 12, "bold"))
            lbl.pack(anchor="w", pady=(12, 4))

        # Header + meta
        add_section(title)
        meta = ttk.Frame(content); meta.pack(fill="x")
        ttk.Label(meta, text=f"Servings: {data.get('servings','')}", padding=(0,0,12,0)).pack(side="left")
        ttk.Label(meta, text=f"Difficulty: {data.get('difficulty','')}").pack(side="left")

        # Time
        t = data.get("time") or {}
        add_section("Time")
        tf = ttk.Frame(content); tf.pack(fill="x")
        ttk.Label(tf, text=f"Prep: {t.get('prep_min','?')} min", padding=(0,0,12,0)).pack(side="left")
        ttk.Label(tf, text=f"Cook: {t.get('cook_min','?')} min", padding=(0,0,12,0)).pack(side="left")
        ttk.Label(tf, text=f"Total: {t.get('total_min','?')} min").pack(side="left")

        # Ingredients table
        add_section("Ingredients")
        ing_frame = ttk.Frame(content); ing_frame.pack(fill="x")
        cols = ("Qty", "Unit", "Ingredient", "Notes")
        tree = ttk.Treeview(ing_frame, columns=cols, show="headings", height=8)
        for c, w in zip(cols, (80, 80, 320, 230)):
            tree.heading(c, text=c)
            tree.column(c, width=w, anchor="w")
        tree.pack(fill="x", expand=False)
        for ing in (data.get("ingredients") or []):
            qty = ing.get("quantity", "")
            unit = ing.get("unit", "")
            name = ing.get("name", "")
            notes = ing.get("notes", "")
            tree.insert("", "end", values=(qty, unit, name, notes))

        # Steps
        add_section("Steps")
        steps = data.get("steps") or []
        for st in steps:
            card = ttk.Frame(content, padding=8, relief="groove")
            card.pack(fill="x", pady=6)
            num = st.get("number", "")
            instr = st.get("instruction", "")
            dur = st.get("duration_min", None)
            header = f"Step {num}"
            if isinstance(dur, int):
                header += f" — {dur} min"
            ttk.Label(card, text=header, font=("Segoe UI", 10, "bold")).pack(anchor="w")
            ttk.Label(card, text=instr, wraplength=740, justify="left").pack(anchor="w", pady=(2, 6))

            equip = st.get("equipment", [])
            if isinstance(equip, list) and equip:
                ef = ttk.Frame(card); ef.pack(fill="x", pady=(2,2))
                ttk.Label(ef, text="Equipment:", font=("Segoe UI", 9, "italic")).pack(side="left")
                eq_texts = []
                for e in equip:
                    nm = e.get("name", "")
                    use = e.get("usage")
                    eq_texts.append(f"{nm}{' ('+use+')' if use else ''}")
                ttk.Label(card, text=", ".join(eq_texts)).pack(anchor="w")

            if st.get("notes"):
                ttk.Label(card, text=f"Notes: {st.get('notes')}", foreground="#555").pack(anchor="w", pady=(2,0))

        # Make sure scrolling bounds are correct initially
        content.update_idletasks()
        on_configure()


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
