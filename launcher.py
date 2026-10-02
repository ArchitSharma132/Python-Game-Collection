import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os
import threading
import ctypes
import ctypes.wintypes as wt
import time as _time

# ==============================================================
#  CONFIG
# ==============================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

CAB       = "#08080E"
SCREEN_BG = "#0C0C1A"
BEZEL     = "#252540"
LAVENDER  = "#B0B0D8"
BLUE      = "#4466FF"
BLUE_HI   = "#6688FF"
DIM       = "#5858A0"
CARD_BG   = "#12122A"
CARD_SEL  = "#1E1E44"
GOLD      = "#FFD700"
RED       = "#CC2244"
RED_HI    = "#FF3366"
GREEN_T   = "#00FF66"
BLACK     = "#000000"

PX = "Terminal"
MENU_W, MENU_H = 660, 560

GAMES = [
    {"name": "SNAKE",      "file": "snake.py",                "desc": "Eat fruit. Grow. Don't crash.",  "icon": ">>", "type": "gui",     "size": (600, 600)},
    {"name": "PONG",       "file": "pong.py",                 "desc": "Paddle ball vs AI.",             "icon": "<>", "type": "gui",     "size": (790, 560)},
    {"name": "BLACKJACK",  "file": "blackjack.py",            "desc": "Hit or Stand. Beat the dealer.", "icon": "BJ", "type": "console"},
    {"name": "CRICKET",    "file": "cricket.py",              "desc": "Pick 1-6. Outscore the CPU.",    "icon": "//", "type": "console"},
    {"name": "DODGEBALL",  "file": "dodgeball.py",            "desc": "Dodge balls. Reach the top.",    "icon": "OO", "type": "gui",     "size": (512, 512)},
    {"name": "ROAD CROSS", "file": "Turtle_road_crossing.py", "desc": "Cross the road. Avoid cars.",    "icon": "==", "type": "gui",     "size": (600, 600)},
]


def px(size, bold=False):
    return (PX, size, "bold" if bold else "normal")


# ==============================================================
#  WIN32 HELPERS  –  find, reparent, attach input
# ==============================================================
_u32 = ctypes.windll.user32
_WNDENUMPROC = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)


def _find_hwnd(pid, timeout=8.0):
    """Wait for *pid* to create a visible top-level window, return its HWND."""
    deadline = _time.time() + timeout
    while _time.time() < deadline:
        found = []

        def _cb(hwnd, _lp):
            p = wt.DWORD()
            _u32.GetWindowThreadProcessId(hwnd, ctypes.byref(p))
            if p.value == pid and _u32.IsWindowVisible(hwnd):
                found.append(hwnd)
            return True

        cb_ref = _WNDENUMPROC(_cb)      # prevent GC during call
        _u32.EnumWindows(cb_ref, 0)
        if found:
            return found[0]
        _time.sleep(0.15)
    return 0


def _embed_hwnd(child, parent, w, h):
    """Strip chrome from *child*, reparent into *parent*, attach keyboard."""
    GWL_STYLE = -16
    WS_CHILD  = 0x40000000

    style = _u32.GetWindowLongW(child, GWL_STYLE)
    style = (style & ~0x00CF0000 & ~0x80000000) | WS_CHILD
    _u32.SetWindowLongW(child, GWL_STYLE, style)

    _u32.SetParent(child, parent)
    _u32.MoveWindow(child, 0, 0, w, h, True)

    # Attach the child's thread-input queue to the parent's
    # so keyboard events reach the embedded window.
    p_tid = _u32.GetWindowThreadProcessId(parent, None)
    c_tid = _u32.GetWindowThreadProcessId(child, None)
    if p_tid and c_tid and p_tid != c_tid:
        _u32.AttachThreadInput(c_tid, p_tid, True)

    _u32.SetFocus(child)


# ==============================================================
#  ARCADE LAUNCHER
# ==============================================================
class ArcadeLauncher:

    def __init__(self, root):
        self.root = root
        self.root.title("PYTHON ARCADE")
        self.root.configure(bg=CAB)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self.proc = None
        self.sel = 0
        self.rows = []

        self._build()
        self._bind_keys()
        self._center(MENU_W, MENU_H)

    def _center(self, w, h):
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

    # ==========================================================
    #  LAYOUT
    # ==========================================================
    def _build(self):
        tk.Frame(self.root, bg=GOLD, height=3).pack(fill="x")

        mq = tk.Frame(self.root, bg=CAB, pady=3)
        mq.pack(fill="x")
        bdr = tk.Frame(mq, bg=BLUE, padx=2, pady=2)
        bdr.pack()
        inner = tk.Frame(bdr, bg=CAB, padx=12, pady=1)
        inner.pack()
        tk.Label(inner, text="PYTHON ARCADE", font=px(14, True),
                 bg=CAB, fg=BLUE).pack()

        tk.Frame(self.root, bg=BEZEL, height=2).pack(fill="x", padx=10)

        bezel = tk.Frame(self.root, bg=BEZEL, padx=3, pady=3)
        bezel.pack(fill="both", expand=True, padx=10, pady=(2, 2))
        self.crt = tk.Frame(bezel, bg=SCREEN_BG)
        self.crt.pack(fill="both", expand=True)

        self.menu_view = tk.Frame(self.crt, bg=SCREEN_BG)
        self.game_view = tk.Frame(self.crt, bg=BLACK)
        self._build_menu()

        tk.Frame(self.root, bg=BEZEL, height=2).pack(fill="x", padx=10)

        cp = tk.Frame(self.root, bg=CAB, pady=4)
        cp.pack(fill="x")
        row = tk.Frame(cp, bg=CAB)
        row.pack()

        self.btn_play = self._btn(row, " PLAY ", RED, RED_HI,
                                  px(11, True), self._play_selected, 3)
        self.btn_play.pack(side="left", padx=5)
        self.btn_back = self._btn(row, " BACK ", BEZEL, BLUE,
                                  px(9), self._back_to_menu, 2)
        self.btn_back.pack(side="left", padx=5)
        self.btn_back.config(state="disabled")
        self.btn_exit = self._btn(row, " EXIT ", BEZEL, BLUE,
                                  px(9), self._on_close, 2)
        self.btn_exit.pack(side="left", padx=5)

        tk.Label(self.root, text="\u2500\u2500 COIN \u2500\u2500",
                 font=px(7), bg=CAB, fg=GOLD).pack(pady=(0, 2))
        tk.Frame(self.root, bg=GOLD, height=3).pack(fill="x", side="bottom")

        self._show_menu()

    def _btn(self, par, txt, bg_c, hov, fnt, cmd, bd):
        b = tk.Button(par, text=txt, font=fnt, bg=bg_c, fg="#FFF",
                      activebackground=hov, activeforeground="#FFF",
                      relief="raised", bd=bd, cursor="hand2",
                      padx=14, pady=2, command=cmd)
        b.bind("<Enter>",
               lambda e: b.config(bg=hov)
               if str(b.cget("state")) != "disabled" else None)
        b.bind("<Leave>", lambda e: b.config(bg=bg_c))
        return b

    # ==========================================================
    #  MENU
    # ==========================================================
    def _build_menu(self):
        hdr = tk.Frame(self.menu_view, bg=SCREEN_BG, pady=3)
        hdr.pack(fill="x")
        tk.Label(hdr, text=">> SELECT GAME <<", font=px(11, True),
                 bg=SCREEN_BG, fg=LAVENDER).pack()
        tk.Frame(self.menu_view, bg=BEZEL, height=1).pack(fill="x", padx=8)

        ctr = tk.Frame(self.menu_view, bg=SCREEN_BG)
        ctr.pack(fill="both", expand=True, padx=4, pady=2)

        self._cvs = tk.Canvas(ctr, bg=SCREEN_BG, highlightthickness=0)
        sb = tk.Scrollbar(ctr, orient="vertical", command=self._cvs.yview,
                          bg=BEZEL, troughcolor=SCREEN_BG, width=8)
        self.lf = tk.Frame(self._cvs, bg=SCREEN_BG)

        self.lf.bind("<Configure>",
                     lambda e: self._cvs.configure(
                         scrollregion=self._cvs.bbox("all")))
        self._cw = self._cvs.create_window(
            (0, 0), window=self.lf, anchor="nw")
        self._cvs.configure(yscrollcommand=sb.set)
        self._cvs.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self._cvs.bind("<Configure>",
                       lambda e: self._cvs.itemconfigure(
                           self._cw, width=e.width))
        self._cvs.bind_all(
            "<MouseWheel>",
            lambda e: self._cvs.yview_scroll(
                int(-1 * (e.delta / 120)), "units"))

        for i, g in enumerate(GAMES):
            self.rows.append(self._row(i, g))

        tk.Frame(self.menu_view, bg=BEZEL, height=1).pack(fill="x", padx=8)
        ft = tk.Frame(self.menu_view, bg=SCREEN_BG, pady=2)
        ft.pack(fill="x")
        tk.Label(ft, text="[UP/DN] Move  [ENTER] Play  [ESC] Quit",
                 font=px(7), bg=SCREEN_BG, fg=DIM).pack()

    def _row(self, idx, g):
        f = tk.Frame(self.lf, bg=CARD_BG, padx=8, pady=4)
        f.pack(fill="x", pady=2, ipady=1)

        ic = tk.Label(f, text=f" {g['icon']} ", font=px(10, True),
                      bg=BLUE, fg="#FFF", padx=2)
        ic.pack(side="left", padx=(0, 8))

        inf = tk.Frame(f, bg=CARD_BG)
        inf.pack(side="left", fill="x", expand=True)
        nm = tk.Label(inf, text=g["name"], font=px(10, True),
                      bg=CARD_BG, fg=LAVENDER, anchor="w")
        nm.pack(fill="x")
        ds = tk.Label(inf, text=g["desc"], font=px(7),
                      bg=CARD_BG, fg=DIM, anchor="w")
        ds.pack(fill="x")

        ar = tk.Label(f, text="", font=px(10, True),
                      bg=CARD_BG, fg=BLUE, padx=4)
        ar.pack(side="right")

        ws = [f, ic, inf, nm, ds, ar]
        for w in ws:
            w.bind("<Button-1>", lambda e, i=idx: self._click(i))
            w.bind("<Enter>", lambda e, i=idx: self._hover(i))

        return {"f": f, "ic": ic, "nm": nm, "ds": ds,
                "ar": ar, "inf": inf, "ws": ws}

    def _upd(self):
        for i, r in enumerate(self.rows):
            s = (i == self.sel)
            bg = CARD_SEL if s else CARD_BG
            for w in r["ws"]:
                w.configure(bg=bg)
            r["nm"].config(fg="#FFF" if s else LAVENDER)
            r["ds"].config(fg=LAVENDER if s else DIM)
            r["ar"].config(text="\u25B6" if s else "", bg=bg)
            r["ic"].config(bg=BLUE_HI if s else BLUE)

    def _hover(self, i):
        self.sel = i
        self._upd()

    def _click(self, i):
        self.sel = i
        self._upd()
        self._play_selected()

    # ==========================================================
    #  VIEW SWITCHING
    # ==========================================================
    def _show_menu(self):
        try:
            self.game_view.pack_forget()
            self.menu_view.pack(fill="both", expand=True)
            if hasattr(self, "btn_play"):
                self.btn_play.config(state="normal")
                self.btn_back.config(state="disabled")
            self._upd()
            self._center(MENU_W, MENU_H)
        except tk.TclError:
            pass

    def _show_game(self):
        self.menu_view.pack_forget()
        for w in self.game_view.winfo_children():
            w.destroy()
        self.game_view.pack(fill="both", expand=True)
        self.btn_play.config(state="disabled")
        self.btn_back.config(state="normal")

    def _fit_game(self, gw, gh):
        self.root.update_idletasks()
        cw = self.crt.winfo_width()
        ch = self.crt.winfo_height()
        ww = self.root.winfo_width()
        wh = self.root.winfo_height()
        chrome_w = ww - cw if cw > 10 else 46
        chrome_h = wh - ch if ch > 10 else 120
        nw = gw + chrome_w + 12
        nh = gh + chrome_h + 12
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        nw = min(nw, sw - 40)
        nh = min(nh, sh - 60)
        self._center(nw, nh)
        self.root.update_idletasks()

    # ==========================================================
    #  KEYBOARD
    # ==========================================================
    def _bind_keys(self):
        self.root.bind("<Up>",     lambda e: self._nav(-1))
        self.root.bind("<Down>",   lambda e: self._nav(1))
        self.root.bind("<Return>", lambda e: self._play_selected())
        self.root.bind("<Escape>", lambda e: self._on_esc())

    def _nav(self, d):
        self.sel = (self.sel + d) % len(GAMES)
        self._upd()

    def _on_esc(self):
        if self.game_view.winfo_ismapped():
            self._back_to_menu()
        else:
            self._on_close()

    # ==========================================================
    #  LAUNCH DISPATCHER
    # ==========================================================
    def _play_selected(self):
        if self.proc is not None:
            return
        g = GAMES[self.sel]
        fp = os.path.join(SCRIPT_DIR, g["file"])
        if not os.path.isfile(fp):
            messagebox.showerror("NOT FOUND", f"Missing:\n{fp}")
            return
        self._show_game()
        if g["type"] == "gui":
            self._run_gui(g, fp)
        else:
            self._run_console(g, fp)

    # ==========================================================
    #  GUI GAMES  (pygame + turtle)  –  Win32 reparent approach
    # ==========================================================
    def _run_gui(self, game, fp):
        gw, gh = game.get("size", (600, 600))
        self._fit_game(gw, gh)

        # Embed frame + hint
        wrapper = tk.Frame(self.game_view, bg=BLACK)
        wrapper.pack(fill="both", expand=True)

        embed = tk.Frame(wrapper, bg=BLACK, width=gw, height=gh)
        embed.pack(expand=True)
        embed.pack_propagate(False)

        hint = tk.Label(wrapper,
                        text="Click game for keyboard input  \u2502  BACK to return",
                        font=px(7), bg=BLACK, fg=DIM)
        hint.pack(side="bottom", pady=(0, 2))

        self.root.update_idletasks()
        self.root.update()

        parent_hwnd = embed.winfo_id()

        # Launch game as a normal subprocess (its own window + event loop)
        self.proc = subprocess.Popen(
            [sys.executable, fp], cwd=SCRIPT_DIR)

        def _do():
            child = _find_hwnd(self.proc.pid)
            if child:
                _embed_hwnd(child, parent_hwnd, gw, gh)
            # Wait for game to exit
            if self.proc:
                self.proc.wait()
            self.proc = None
            self.root.after(100, self._show_menu)

        threading.Thread(target=_do, daemon=True).start()

    # ==========================================================
    #  CONSOLE GAMES  –  embedded green-screen terminal
    # ==========================================================
    def _run_console(self, game, fp):
        self._fit_game(620, 480)

        frame = tk.Frame(self.game_view, bg="#06060E")
        frame.pack(fill="both", expand=True)

        tbar = tk.Frame(frame, bg=CARD_BG, pady=2)
        tbar.pack(fill="x")
        tk.Label(tbar, text=f"  {game['name']}  ", font=px(9, True),
                 bg=CARD_BG, fg=LAVENDER).pack(side="left", padx=4)

        out_f = tk.Frame(frame, bg="#06060E")
        out_f.pack(fill="both", expand=True)
        out_sb = tk.Scrollbar(out_f, bg=BEZEL, troughcolor="#06060E", width=8)
        out_sb.pack(side="right", fill="y")
        out = tk.Text(out_f, bg="#06060E", fg=GREEN_T, font=px(9),
                      wrap="word", bd=0, padx=8, pady=6,
                      insertbackground=GREEN_T, selectbackground=BLUE,
                      yscrollcommand=out_sb.set)
        out.pack(fill="both", expand=True)
        out_sb.config(command=out.yview)

        ibar = tk.Frame(frame, bg="#0C0C1A", pady=3)
        ibar.pack(fill="x")
        tk.Label(ibar, text=">", font=px(10, True),
                 bg="#0C0C1A", fg=GREEN_T).pack(side="left", padx=(8, 4))
        ent = tk.Entry(ibar, bg="#0C0C1A", fg=GREEN_T, font=px(10),
                       insertbackground=GREEN_T, bd=0, relief="flat")
        ent.pack(side="left", fill="x", expand=True, padx=(0, 8), pady=2)
        ent.focus_set()

        # Binary mode so os.read returns data immediately (no line buffering)
        self.proc = subprocess.Popen(
            [sys.executable, "-u", fp], cwd=SCRIPT_DIR,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)

        def _put(t):
            try:
                if out.winfo_exists():
                    out.insert("end", t)
                    out.see("end")
            except tk.TclError:
                pass

        def _read():
            try:
                fd = self.proc.stdout.fileno()
                while True:
                    data = os.read(fd, 4096)
                    if not data:
                        break
                    txt = data.decode("utf-8", errors="replace")
                    self.root.after(0, lambda t=txt: _put(t))
            except (OSError, ValueError):
                pass
            self.root.after(0, lambda: _put(
                "\n\n--- GAME ENDED --- click BACK to return ---\n"))
            self.proc = None

        def _send(event=None):
            t = ent.get()
            ent.delete(0, "end")
            _put(t + "\n")
            if self.proc and self.proc.stdin:
                try:
                    self.proc.stdin.write((t + "\n").encode("utf-8"))
                    self.proc.stdin.flush()
                except Exception:
                    pass

        ent.bind("<Return>", _send)
        out.bind("<Button-1>", lambda e: self.root.after(10, ent.focus_set))

        threading.Thread(target=_read, daemon=True).start()

    # ==========================================================
    #  NAVIGATION
    # ==========================================================
    def _back_to_menu(self):
        if self.proc:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=3)
            except Exception:
                try:
                    self.proc.kill()
                except Exception:
                    pass
            self.proc = None
        for w in self.game_view.winfo_children():
            try:
                w.destroy()
            except tk.TclError:
                pass
        self._show_menu()

    def _on_close(self):
        if self.proc:
            try:
                self.proc.kill()
            except Exception:
                pass
            self.proc = None
        self.root.destroy()


# ==============================================================
if __name__ == "__main__":
    root = tk.Tk()
    ArcadeLauncher(root)
    root.mainloop()