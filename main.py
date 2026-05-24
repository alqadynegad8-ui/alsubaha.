import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import arabic_reshaper
from bidi.algorithm import get_display
from datetime import datetime
import json
import os

# --- إضافة ميزة الحفظ ---
DATA_FILE = "negad_data.json"

def save_state(self):
    data = {
        "price": self.price_ent.get(),
        "pumps": [(v[0].get(), v[1].get()) for v in self.pump_vars],
        "cash": [v.get() for v in self.cash_vars],
        "expenses": self.expenses
    }
    with open(DATA_FILE, "w") as f: json.dump(data, f)

def load_state(self):
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            self.price_ent.delete(0, 'end'); self.price_ent.insert(0, data.get("price", "475"))
            for i, (v1, v2) in enumerate(data.get("pumps", [])):
                self.pump_vars[i][0].set(v1); self.pump_vars[i][1].set(v2)
            for i, val in enumerate(data.get("cash", [])):
                self.cash_vars[i].set(val)
            for exp in data.get("expenses", []):
                self.tree.insert("", "end", values=(exp['amt'], exp['note']))
                self.expenses.append(exp)
# -----------------------

# إعدادات الألوان الفخمة
BG_COLOR = "#050a0f"
PANEL_COLOR = "#0f172a"
ACCENT_CYAN = "#00f2ff"
ACCENT_GREEN = "#00ff88"

def fix_text(text):
    if not text: return ""
    return get_display(arabic_reshaper.reshape(text))

class NegadFullSystem:
    def __init__(self, root):
        self.root = root
        self.root.title(fix_text("نظام نجاد المتكامل - حساب اللترات"))
        self.root.geometry("550x1000")
        self.root.configure(bg=BG_COLOR)

        self.expenses = []

        # الحاوية الرئيسية
        self.main = tk.Frame(root, bg=BG_COLOR)
        self.main.pack(fill="both", expand=True, padx=15, pady=5)

        # 1. العنوان والتاريخ
        tk.Label(self.main, text=fix_text("شركة النفط اليمنية"), font=("Arial", 22, "bold"), bg=BG_COLOR, fg=ACCENT_CYAN).pack(pady=5)
        tk.Label(self.main, text=datetime.now().strftime("%Y-%m-%d"), bg=BG_COLOR, fg=ACCENT_GREEN, font=("Arial", 12)).pack()

        # 2. بيانات المحضر
        top_p = tk.Frame(self.main, bg=PANEL_COLOR, padx=10, pady=10, highlightthickness=1, highlightbackground="#1e293b")
        top_p.pack(fill="x", pady=5)
        
        r1 = tk.Frame(top_p, bg=PANEL_COLOR); r1.pack(fill="x")
        self.worker = self.create_input(r1, "العامل:", "نجاد")
        self.shift = self.create_input(r1, "الوردية:", "الأولى")

        r2 = tk.Frame(top_p, bg=PANEL_COLOR); r2.pack(fill="x", pady=5)
        self.price_ent = tk.Entry(r2, width=10, justify="center", font=("Arial", 12, "bold"))
        self.price_ent.insert(0, "475")
        self.price_ent.pack(side="right")
        self.price_ent.bind("<KeyRelease>", lambda e: [self.calculate(), save_state(self)])
        tk.Label(r2, text=fix_text("السعر:"), bg=PANEL_COLOR, fg=ACCENT_CYAN).pack(side="right", padx=5)

        # 3. جرد المضخات وحساب اللترات لكل واحدة
        pump_p = tk.Frame(self.main, bg=PANEL_COLOR, highlightthickness=1, highlightbackground="#1e293b", pady=5)
        pump_p.pack(fill="x", pady=5)
        
        self.pump_vars = []
        self.pump_liter_labels = []
        
        for i in range(2):
            v_pre, v_post = tk.StringVar(value="0"), tk.StringVar(value="0")
            v_pre.trace_add("write", lambda *args: [self.calculate(), save_state(self)]); v_post.trace_add("write", lambda *args: [self.calculate(), save_state(self)])
            self.pump_vars.append((v_pre, v_post))
            
            r = tk.Frame(pump_p, bg=PANEL_COLOR, pady=5); r.pack(fill="x", padx=10)
            tk.Label(r, text=fix_text(f"مضخة {i+1}"), bg=PANEL_COLOR, fg=ACCENT_CYAN, width=7).pack(side="right")
            
            self.add_pump_field(r, v_post, "لاحق")
            self.add_pump_field(r, v_pre, "سابق")
            
            v_lit = tk.StringVar(value="0 لتر")
            self.pump_liter_labels.append(v_lit)
            tk.Label(r, textvariable=v_lit, bg="#001a1a", fg=ACCENT_GREEN, font=("Arial", 10, "bold"), width=10).pack(side="left", padx=5)

        # 4. النقدية
        cash_p = tk.Frame(self.main, bg=PANEL_COLOR, highlightthickness=1, highlightbackground="#1e293b", pady=5)
        cash_p.pack(fill="x", pady=5)
        self.cash_vars = []
        cats = ["١٠٠٠", "٥٠٠", "٢٥٠", "٢٠٠", "١٠٠", "أفلاس"]
        for cat in cats:
            v = tk.StringVar(value="0"); v.trace_add("write", lambda *args: [self.calculate(), save_state(self)]); self.cash_vars.append(v)
            r = tk.Frame(cash_p, bg=PANEL_COLOR); r.pack(fill="x", padx=10)
            tk.Label(r, text=fix_text(cat), bg=PANEL_COLOR, fg="white", width=8, anchor="e").pack(side="right")
            tk.Entry(r, textvariable=v, justify="center", font=("Arial", 10)).pack(side="left", fill="x", expand=True, padx=20)

        # 5. الملاحظات
        exp_p = tk.Frame(self.main, bg=PANEL_COLOR, highlightthickness=1, highlightbackground="#1e293b", pady=5)
        exp_p.pack(fill="x", pady=5)
        in_r = tk.Frame(exp_p, bg=PANEL_COLOR); in_r.pack(fill="x", padx=10)
        self.note_in = tk.Entry(in_r, justify="right"); self.note_in.pack(side="right", expand=True, fill="x", padx=2)
        self.amt_in = tk.Entry(in_r, width=10, justify="center", fg="red"); self.amt_in.pack(side="right", padx=2)
        tk.Button(in_r, text=fix_text("إضافة"), command=lambda: [self.add_exp(), save_state(self)], bg=ACCENT_GREEN).pack(side="left")

        list_r = tk.Frame(exp_p, bg=PANEL_COLOR); list_r.pack(fill="x", pady=5, padx=10)
        self.tree = ttk.Treeview(list_r, columns=("a", "n"), show="headings", height=3)
        self.tree.heading("a", text=fix_text("المبلغ")); self.tree.heading("n", text=fix_text("البيان"))
        self.tree.column("a", width=80, anchor="center"); self.tree.column("n", width=200, anchor="e")
        self.tree.pack(side="right", fill="x", expand=True)

        edit_f = tk.Frame(list_r, bg=PANEL_COLOR); edit_f.pack(side="left", padx=5)
        tk.Button(edit_f, text="🗑", command=lambda: [self.del_exp(), save_state(self)], bg="#ff0055", fg="white", width=3).pack(pady=2)
        tk.Button(edit_f, text="📝", command=self.edit_exp, bg=ACCENT_CYAN, width=3).pack(pady=2)

        # 6. الملخص
        res_p = tk.Frame(self.main, bg="#001a1a", highlightthickness=1, highlightbackground=ACCENT_CYAN, pady=10)
        res_p.pack(fill="x", pady=10)
        self.v_liters, self.v_sales, self.v_final = tk.StringVar(value="0"), tk.StringVar(value="0.00"), tk.StringVar(value="0.00")
        
        self.draw_res(res_p, "إجمالي اللترات:", self.v_liters, ACCENT_GREEN)
        self.draw_res(res_p, "إجمالي المبيعات:", self.v_sales, ACCENT_CYAN)
        self.draw_res(res_p, "الفارق النهائي:", self.v_final, "white", True)

        btn_r = tk.Frame(self.main, bg=BG_COLOR); btn_r.pack(fill="x", side="bottom", pady=10)
        tk.Button(btn_r, text=fix_text("حفظ وأرشفة المحضر"), command=lambda: messagebox.showinfo("تم", "تم الحفظ"), bg=ACCENT_CYAN, font=("Arial", 12, "bold"), pady=10).pack(side="right", expand=True, fill="x", padx=5)
        tk.Button(btn_r, text=fix_text("تصفير"), command=lambda: [self.clear_all(), save_state(self)], bg="#ff0055", fg="white", width=10).pack(side="left", padx=5)

        # تحميل البيانات عند التشغيل
        load_state(self)
        self.calculate()

    # --- باقي دوالك كما هي تماماً بدون تغيير ---
    def create_input(self, parent, lbl, default):
        f = tk.Frame(parent, bg=PANEL_COLOR); f.pack(side="right", expand=True, fill="x", padx=5)
        tk.Label(f, text=fix_text(lbl), bg=PANEL_COLOR, fg="#94a3b8", font=("Arial", 9)).pack(side="right")
        e = tk.Entry(f, justify="right"); e.insert(0, default); e.pack(side="right", expand=True, fill="x")
        return e

    def add_pump_field(self, row, var, lbl):
        tk.Entry(row, textvariable=var, width=10, justify="center", font=("Arial", 10, "bold")).pack(side="right", padx=2)
        tk.Label(row, text=fix_text(lbl + ":"), bg=PANEL_COLOR, fg="#94a3b8", font=("Arial", 8)).pack(side="right")

    def draw_res(self, parent, txt, var, clr, bold=False):
        r = tk.Frame(parent, bg="#001a1a"); r.pack(fill="x", padx=15)
        tk.Label(r, text=fix_text(txt), bg="#001a1a", fg="#94a3b8").pack(side="right")
        tk.Label(r, textvariable=var, bg="#001a1a", fg=clr, font=("Arial", 14 if bold else 11, "bold")).pack(side="left")

    def calculate(self, *args):
        try:
            price = float(self.price_ent.get() or 0)
            total_l = 0
            for i, pv in enumerate(self.pump_vars):
                lits = float(pv[1].get() or 0) - float(pv[0].get() or 0)
                total_l += lits
                self.pump_liter_labels[i].set(f"{lits:,.0f} لتر")
            sales = total_l * price
            cash = sum(float(v.get() or 0) for v in self.cash_vars)
            exps = sum(i['amt'] for i in self.expenses)
            self.v_liters.set(f"{total_l:,.2f}")
            self.v_sales.set(f"{sales:,.2f}")
            self.v_final.set(f"{(cash + exps) - sales:,.2f}")
        except: pass

    def add_exp(self):
        n, a = self.note_in.get(), self.amt_in.get()
        if n and a:
            self.tree.insert("", "end", values=(a, n))
            self.expenses.append({"note": n, "amt": float(a)})
            self.note_in.delete(0, 'end'); self.amt_in.delete(0, 'end'); self.calculate()

    def del_exp(self):
        sel = self.tree.selection()
        if sel:
            for i in sel:
                v = self.tree.item(i)['values']
                self.expenses = [x for x in self.expenses if not (x['note'] == v[1] and x['amt'] == float(v[0]))]
                self.tree.delete(i)
            self.calculate()

    def edit_exp(self):
        sel = self.tree.selection()
        if sel:
            v = self.tree.item(sel[0])['values']
            self.note_in.insert(0, v[1]); self.amt_in.insert(0, v[0]); self.del_exp()

    def clear_all(self):
        if messagebox.askyesno("تصفير", "حذف الكل؟"):
            if os.path.exists(DATA_FILE): os.remove(DATA_FILE)
            for pv in self.pump_vars: pv[0].set("0"); pv[1].set("0")
            for v in self.cash_vars: v.set("0")
            for i in self.tree.get_children(): self.tree.delete(i)
            self.expenses = []; self.calculate()

if __name__ == "__main__":
    root = tk.Tk(); app = NegadFullSystem(root); root.mainloop()
