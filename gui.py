
import os, json, tkinter as tk
from tkinter import ttk, messagebox
from ai_client.client import AIClient
from ai_client.ai_request import AIRequest
from ai_client.recipe_schema import schema_description
from ai_client.supported_models import get_supported_models

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

def main():
    root = tk.Tk()
    App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
