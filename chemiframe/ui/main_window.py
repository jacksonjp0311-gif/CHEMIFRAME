import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Any, Dict, List, Optional

from chemiframe.intent.schema import default_intent
from chemiframe.demo_support import run_pipeline
from chemiframe.intent.parser import load_intent
from chemiframe.workspace import repo_root


BG = "#0a0f14"
PANEL = "#111821"
PANEL_2 = "#17212b"
PANEL_3 = "#0f141b"
TEXT = "#e6edf3"
MUTED = "#9db0c3"
ACCENT = "#59c1ff"
ACCENT_2 = "#7ee787"
ACCENT_3 = "#d2a8ff"
ACCENT_4 = "#ffa657"
BORDER = "#283341"
ERROR = "#ff7b72"


class ChemiframeApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("CHEMIFRAME")
        self.geometry("1480x920")
        self.minsize(1280, 800)
        self.configure(bg=BG)

        self.intent_data = default_intent()
        self.repo_root = repo_root()
        self.artifacts_root = self.repo_root / "artifacts"
        self.last_report: Optional[Dict[str, Any]] = None
        self.badge_labels: Dict[str, tk.Label] = {}
        self.run_history_index: List[Path] = []
        self.artifact_index: List[Path] = []

        self._setup_style()
        self._build()
        self._sync_form_from_intent()
        self.refresh_artifacts()
        self.refresh_run_history()

    def _setup_style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("CF.TCombobox", fieldbackground=PANEL_2, background=PANEL_2, foreground=TEXT, arrowcolor=ACCENT)

    def _build(self) -> None:
        self._build_header()
        self._build_controls()
        self._build_main()
        self._build_footer()

    def _build_header(self) -> None:
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=16, pady=14)

        self.logo_canvas = tk.Canvas(
            header,
            width=980,
            height=150,
            bg=BG,
            bd=0,
            highlightthickness=0
        )
        self.logo_canvas.pack(anchor="w")
        self._draw_logo(self.logo_canvas)

    def _draw_logo(self, canvas: tk.Canvas) -> None:
        canvas.delete("all")

        block = 12
        gap = 2
        x0 = 10
        y0 = 28
        palette = [ACCENT, ACCENT_2, ACCENT_3, ACCENT_4]

        glyphs = {
            "C": ["11111","10000","10000","10000","10000","10000","11111"],
            "H": ["10001","10001","10001","11111","10001","10001","10001"],
            "E": ["11111","10000","10000","11110","10000","10000","11111"],
            "M": ["10001","11011","10101","10101","10001","10001","10001"],
            "I": ["11111","00100","00100","00100","00100","00100","11111"],
            "F": ["11111","10000","10000","11110","10000","10000","10000"],
            "R": ["11110","10001","10001","11110","10100","10010","10001"],
            "A": ["01110","10001","10001","11111","10001","10001","10001"],
        }

        word = "CHEMIFRAME"
        x = x0
        for idx, ch in enumerate(word):
            glyph = glyphs[ch]
            color = palette[idx % len(palette)]
            for row, row_bits in enumerate(glyph):
                for col, bit in enumerate(row_bits):
                    if bit == "1":
                        x1 = x + col * (block + gap)
                        y1 = y0 + row * (block + gap)
                        x2 = x1 + block
                        y2 = y1 + block
                        canvas.create_rectangle(
                            x1, y1, x2, y2,
                            fill=color,
                            outline=PANEL_2,
                            width=1
                        )
            x += 5 * (block + gap) + 10

        canvas.create_line(12, 122, 550, 122, fill=MUTED, width=2)
        canvas.create_text(
            16, 128,
            anchor="nw",
            text="PROGRAM THE MATTER. PRESERVE THE TRACE.",
            fill=TEXT,
            font=("Consolas", 12, "bold")
        )
        canvas.create_text(
            16, 4,
            anchor="nw",
            text="human-facing scientific programming shell",
            fill=MUTED,
            font=("Segoe UI", 9)
        )

    def _build_controls(self) -> None:
        control_bar = tk.Frame(self, bg=BG)
        control_bar.pack(fill="x", padx=16, pady=6)

        self._button(control_bar, "Load Intent", self.load_intent_file).pack(side="left", padx=4)
        self._button(control_bar, "Reset", self.reset_intent).pack(side="left", padx=4)
        self._button(control_bar, "Apply Form -> Intent", self.apply_form_to_intent).pack(side="left", padx=4)
        self._button(control_bar, "Run Selected Mode", self.run_selected_mode).pack(side="left", padx=4)
        self._button(control_bar, "Refresh Browser", self.refresh_all_panels).pack(side="left", padx=4)

    def _build_main(self) -> None:
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=16, pady=10)

        top_row = tk.Frame(body, bg=BG)
        top_row.pack(fill="both", expand=True)

        left = tk.Frame(top_row, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        center = tk.Frame(top_row, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        right = tk.Frame(top_row, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)

        left.pack(side="left", fill="y", padx=(0, 8))
        center.pack(side="left", fill="both", expand=True, padx=8)
        right.pack(side="left", fill="both", expand=True, padx=(8, 0))

        self._card_header(left, "Interaction Surface", "Human-first scientific controls")
        self._card_header(center, "Intent JSON", "Advanced editable intent surface")
        self._card_header(right, "Output / Trace", "Compiled and audited runtime state")

        self._build_form_panel(left)
        self._build_intent_panel(center)
        self._build_output_panel(right)

        lower = tk.Frame(body, bg=BG)
        lower.pack(fill="both", expand=True, pady=14)

        browser = tk.Frame(lower, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        history = tk.Frame(lower, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        badges = tk.Frame(lower, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)

        browser.pack(side="left", fill="both", expand=True, padx=(0, 8))
        history.pack(side="left", fill="both", expand=True, padx=8)
        badges.pack(side="left", fill="both", expand=True, padx=(8, 0))

        self._card_header(browser, "Artifact Browser", "Compiled files, contracts, traces, reports")
        self._card_header(history, "Run History", "Recent reports and execution outcomes")
        self._card_header(badges, "Validation Badges", "Visible contract state")

        self._build_artifact_browser(browser)
        self._build_run_history(history)
        self._build_badges_panel(badges)

    def _card_header(self, parent: tk.Widget, title: str, subtitle: str) -> None:
        hdr = tk.Frame(parent, bg=PANEL)
        hdr.pack(fill="x", padx=12, pady=10)
        tk.Label(hdr, text=title, bg=PANEL, fg=TEXT, font=("Segoe UI", 12, "bold")).pack(anchor="w")
        tk.Label(hdr, text=subtitle, bg=PANEL, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", pady=2)

    def _build_form_panel(self, parent: tk.Widget) -> None:
        form = tk.Frame(parent, bg=PANEL_2)
        form.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.target_family_var = tk.StringVar()
        self.target_domain_var = tk.StringVar()
        self.blueprint_var = tk.StringVar()
        self.run_mode_var = tk.StringVar(value="hardware")
        self.inputs_var = tk.StringVar()
        self.sequence_var = tk.StringVar()
        self.objectives_var = tk.StringVar()
        self.max_steps_var = tk.StringVar()
        self.detectability_var = tk.StringVar()
        self.green_only_var = tk.BooleanVar(value=True)

        inner = tk.Frame(form, bg=PANEL_2)
        inner.pack(fill="both", expand=True, padx=12, pady=12)

        row = 0
        self._field_label(inner, "Target Family", row)
        self._entry(inner, self.target_family_var, row)

        row += 1
        self._field_label(inner, "Target Domain", row)
        self._combo(inner, self.target_domain_var, [
            "small_molecule",
            "sequence_defined_biopolymer",
            "oligonucleotide_synthesis",
            "hybrid_chemo_bio"
        ], row)

        row += 1
        self._field_label(inner, "Blueprint Mode", row)
        self._combo(inner, self.blueprint_var, [
            "auto",
            "aryl_coupling",
            "sequence_assembly",
            "hybrid_chemo_bio"
        ], row)

        row += 1
        self._field_label(inner, "Run Mode", row)
        self._combo(inner, self.run_mode_var, ["hardware", "simulated"], row)

        row += 1
        self._field_label(inner, "Inputs (comma-separated)", row)
        self._entry(inner, self.inputs_var, row)

        row += 1
        self._field_label(inner, "Sequence (comma-separated)", row)
        self._entry(inner, self.sequence_var, row)

        row += 1
        self._field_label(inner, "Objectives (comma-separated)", row)
        self._entry(inner, self.objectives_var, row)

        row += 1
        self._field_label(inner, "Max Steps", row)
        self._entry(inner, self.max_steps_var, row)

        row += 1
        self._field_label(inner, "Min Detectability", row)
        self._entry(inner, self.detectability_var, row)

        row += 1
        cb_wrap = tk.Frame(inner, bg=PANEL_2)
        cb_wrap.grid(row=row, column=0, columnspan=2, sticky="w", pady=10)
        tk.Checkbutton(
            cb_wrap,
            text="Green solvents only",
            variable=self.green_only_var,
            bg=PANEL_2,
            fg=TEXT,
            activebackground=PANEL_2,
            activeforeground=TEXT,
            selectcolor=PANEL_3,
            font=("Segoe UI", 10)
        ).pack(anchor="w")

        row += 1
        hint = tk.Label(
            inner,
            text="Use the form for normal interaction. Use the JSON panel for advanced editing.",
            bg=PANEL_2,
            fg=MUTED,
            wraplength=320,
            justify="left",
            font=("Segoe UI", 9)
        )
        hint.grid(row=row, column=0, columnspan=2, sticky="w", pady=14)

    def _build_intent_panel(self, parent: tk.Widget) -> None:
        frame = tk.Frame(parent, bg=PANEL_2)
        frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.intent_text = tk.Text(
            frame,
            wrap="word",
            bg=PANEL_2,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            borderwidth=0,
            font=("Consolas", 11),
            selectbackground="#264f78",
            selectforeground=TEXT
        )
        self.intent_text.pack(fill="both", expand=True, padx=10, pady=10)

    def _build_output_panel(self, parent: tk.Widget) -> None:
        frame = tk.Frame(parent, bg=PANEL_2)
        frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.output_text = tk.Text(
            frame,
            wrap="word",
            bg=PANEL_2,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            borderwidth=0,
            font=("Consolas", 11),
            selectbackground="#264f78",
            selectforeground=TEXT
        )
        self.output_text.pack(fill="both", expand=True, padx=10, pady=10)

    def _build_artifact_browser(self, parent: tk.Widget) -> None:
        frame = tk.Frame(parent, bg=PANEL_2)
        frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.artifact_list = tk.Listbox(
            frame,
            bg=PANEL_3,
            fg=TEXT,
            selectbackground="#264f78",
            selectforeground=TEXT,
            relief="flat",
            borderwidth=0,
            font=("Consolas", 10),
            height=10
        )
        self.artifact_list.pack(fill="both", expand=True, padx=10, pady=10)
        self.artifact_list.bind("<<ListboxSelect>>", self.open_selected_artifact)

        btns = tk.Frame(frame, bg=PANEL_2)
        btns.pack(fill="x", padx=10, pady=(0, 10))
        self._button(btns, "Open Selected Artifact", self.open_selected_artifact).pack(side="left", padx=4)
        self._button(btns, "Refresh", self.refresh_artifacts).pack(side="left", padx=4)

    def _build_run_history(self, parent: tk.Widget) -> None:
        frame = tk.Frame(parent, bg=PANEL_2)
        frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.history_list = tk.Listbox(
            frame,
            bg=PANEL_3,
            fg=TEXT,
            selectbackground="#264f78",
            selectforeground=TEXT,
            relief="flat",
            borderwidth=0,
            font=("Consolas", 10),
            height=10
        )
        self.history_list.pack(fill="both", expand=True, padx=10, pady=10)
        self.history_list.bind("<<ListboxSelect>>", self.open_selected_history)

        btns = tk.Frame(frame, bg=PANEL_2)
        btns.pack(fill="x", padx=10, pady=(0, 10))
        self._button(btns, "Open Selected Run", self.open_selected_history).pack(side="left", padx=4)
        self._button(btns, "Refresh", self.refresh_run_history).pack(side="left", padx=4)

    def _build_badges_panel(self, parent: tk.Widget) -> None:
        frame = tk.Frame(parent, bg=PANEL_2)
        frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        inner = tk.Frame(frame, bg=PANEL_2)
        inner.pack(fill="both", expand=True, padx=12, pady=12)

        keys = [
            "detectability_ok",
            "assembly_bound_ok",
            "dec_points_defined",
            "route_admissible",
            "trace_schema_ok",
            "ok",
        ]

        for key in keys:
            row = tk.Frame(inner, bg=PANEL_2)
            row.pack(fill="x", pady=4)

            tk.Label(
                row,
                text=key,
                bg=PANEL_2,
                fg=MUTED,
                font=("Segoe UI", 9, "bold"),
                width=20,
                anchor="w"
            ).pack(side="left")

            badge = tk.Label(
                row,
                text="-",
                bg=PANEL_3,
                fg=TEXT,
                font=("Segoe UI", 9, "bold"),
                padx=10,
                pady=4
            )
            badge.pack(side="left")
            self.badge_labels[key] = badge

    def _build_footer(self) -> None:
        footer = tk.Frame(self, bg=BG)
        footer.pack(fill="x", padx=16, pady=10)

        self.status_var = tk.StringVar(value="Ready.")
        tk.Label(
            footer,
            textvariable=self.status_var,
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 9)
        ).pack(anchor="w")

    def _field_label(self, parent: tk.Widget, text: str, row: int) -> None:
        tk.Label(parent, text=text, bg=PANEL_2, fg=MUTED, font=("Segoe UI", 9, "bold")).grid(
            row=row, column=0, sticky="w", pady=4
        )

    def _entry(self, parent: tk.Widget, var: tk.StringVar, row: int) -> None:
        e = tk.Entry(
            parent,
            textvariable=var,
            bg=PANEL_3,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
            font=("Segoe UI", 10),
            width=36
        )
        e.grid(row=row, column=1, sticky="ew", pady=6)
        parent.grid_columnconfigure(1, weight=1)

    def _combo(self, parent: tk.Widget, var: tk.StringVar, values, row: int) -> None:
        combo = ttk.Combobox(
            parent,
            textvariable=var,
            values=list(values),
            state="readonly",
            style="CF.TCombobox",
            width=33
        )
        combo.grid(row=row, column=1, sticky="ew", pady=6)
        if values and not var.get():
            var.set(values[0])

    def _button(self, parent: tk.Widget, label: str, command):
        return tk.Button(
            parent,
            text=label,
            command=command,
            bg=PANEL,
            fg=TEXT,
            activebackground=ACCENT,
            activeforeground=BG,
            relief="flat",
            bd=0,
            padx=12,
            pady=8,
            font=("Segoe UI", 10, "bold"),
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT
        )

    def _set_text(self, widget: tk.Text, value: str) -> None:
        widget.delete("1.0", "end")
        widget.insert("1.0", value)

    def _sync_form_from_intent(self) -> None:
        intent = self.intent_data
        constraints = intent.get("constraints", {})

        self.target_family_var.set(intent.get("target_family", ""))
        self.target_domain_var.set(intent.get("target_domain", "small_molecule"))
        self.blueprint_var.set(intent.get("blueprint_mode", "auto"))
        self.inputs_var.set(", ".join(intent.get("inputs", [])))
        self.sequence_var.set(", ".join(intent.get("sequence", [])))
        self.objectives_var.set(", ".join(intent.get("objectives", [])))
        self.max_steps_var.set(str(constraints.get("max_steps", "")))
        self.detectability_var.set(str(constraints.get("min_detectability_score", "")))
        self.green_only_var.set(bool(constraints.get("green_solvents_only", True)))

        self._set_text(self.intent_text, json.dumps(self.intent_data, indent=2))
        self._set_text(self.output_text, self._welcome_text())
        self._clear_badges()

    def _welcome_text(self) -> str:
        return json.dumps(
            {
                "application": "CHEMIFRAME",
                "theme": "dark-multicolor",
                "tagline": "PROGRAM THE MATTER. PRESERVE THE TRACE.",
                "interaction_mode": "human-facing scientific shell",
                "surfaces": {
                    "artifact_browser": "present",
                    "validation_badges": "present",
                    "run_history": "present"
                }
            },
            indent=2
        )

    def apply_form_to_intent(self) -> None:
        try:
            inputs = [x.strip() for x in self.inputs_var.get().split(",") if x.strip()]
            sequence = [x.strip() for x in self.sequence_var.get().split(",") if x.strip()]
            objectives = [x.strip() for x in self.objectives_var.get().split(",") if x.strip()]

            constraints = {
                "max_steps": int(self.max_steps_var.get()) if self.max_steps_var.get().strip() else 6,
                "green_solvents_only": bool(self.green_only_var.get()),
                "min_detectability_score": float(self.detectability_var.get()) if self.detectability_var.get().strip() else 0.90,
            }

            intent = {
                "target_family": self.target_family_var.get().strip() or "unnamed_program",
                "target_domain": self.target_domain_var.get().strip() or "small_molecule",
                "blueprint_mode": self.blueprint_var.get().strip() or "auto",
                "inputs": inputs,
                "constraints": constraints,
                "objectives": objectives,
            }

            if sequence:
                intent["sequence"] = sequence

            if intent["target_domain"] == "hybrid_chemo_bio":
                intent["chemical_segment"] = [
                    "charge_precursors",
                    "execute_primary_transformation",
                    "verify_interface_state"
                ]
                intent["interface_state"] = {
                    "state_id": "iface_001",
                    "detectable": True,
                    "validated": True
                }
                intent["bio_segment"] = [
                    "bounded_delivery",
                    "bio_readout_checkpoint"
                ]

            self.intent_data = intent
            self._set_text(self.intent_text, json.dumps(self.intent_data, indent=2))
            self.status_var.set("Form applied to intent.")
        except Exception as exc:
            messagebox.showerror("Form error", str(exc))
            self.status_var.set("Form apply failed.")

    def reset_intent(self) -> None:
        self.intent_data = default_intent()
        self._sync_form_from_intent()
        self.status_var.set("Intent reset to default.")

    def load_intent_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Select intent file",
            filetypes=[
                ("Intent files", "*.json *.yaml *.yml"),
                ("All files", "*.*")
            ]
        )
        if not path:
            return
        try:
            self.intent_data = load_intent(path)
            self._sync_form_from_intent()
            self.status_var.set(f"Loaded intent: {Path(path).name}")
        except Exception as exc:
            messagebox.showerror("Load failed", str(exc))
            self.status_var.set("Load failed.")

    def _intent_from_editor(self):
        raw = self.intent_text.get("1.0", "end").strip()
        try:
            return json.loads(raw)
        except Exception:
            return self.intent_data

    def run_selected_mode(self) -> None:
        simulate = self.run_mode_var.get().strip().lower() == "simulated"
        self._run(simulate=simulate)

    def _run(self, simulate: bool) -> None:
        try:
            intent = self._intent_from_editor()
            report = run_pipeline(intent, simulate=simulate)
            self.last_report = report
            self._set_text(self.output_text, json.dumps(report, indent=2))
            self._update_badges(report.get("contracts", {}))
            self.refresh_artifacts()
            self.refresh_run_history()
            mode = "simulated" if simulate else "hardware"
            self.status_var.set(f"Run complete ({mode}) - {report['run_id']}")
        except Exception as exc:
            messagebox.showerror("Run failed", str(exc))
            self.status_var.set("Run failed.")

    def _clear_badges(self) -> None:
        for label in self.badge_labels.values():
            label.configure(text="-", bg=PANEL_3, fg=TEXT)

    def _update_badges(self, contracts: Dict[str, Any]) -> None:
        for key, label in self.badge_labels.items():
            value = contracts.get(key, None)
            if value is True:
                label.configure(text="PASS", bg=ACCENT_2, fg=BG)
            elif value is False:
                label.configure(text="FAIL", bg=ERROR, fg=BG)
            else:
                label.configure(text="-", bg=PANEL_3, fg=TEXT)

    def refresh_all_panels(self) -> None:
        self.refresh_artifacts()
        self.refresh_run_history()
        self.status_var.set("Browsers refreshed.")

    def refresh_artifacts(self) -> None:
        self.artifact_list.delete(0, "end")
        self.artifact_index = []

        folders = [
            self.artifacts_root / "compiled_xdl",
            self.artifacts_root / "contracts",
            self.artifacts_root / "traces",
            self.artifacts_root / "reports",
            self.artifacts_root / "simulator_runs",
            self.artifacts_root / "sequence_artifacts",
            self.artifacts_root / "hybrid_artifacts",
        ]

        for folder in folders:
            if folder.exists():
                for path in sorted(folder.glob("*"), key=lambda p: p.stat().st_mtime, reverse=True):
                    self.artifact_index.append(path)
                    self.artifact_list.insert("end", f"{folder.name} :: {path.name}")

    def refresh_run_history(self) -> None:
        self.history_list.delete(0, "end")
        self.run_history_index = []

        reports_dir = self.artifacts_root / "reports"
        if reports_dir.exists():
            for path in sorted(reports_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
                self.run_history_index.append(path)
                try:
                    data = json.loads(path.read_text(encoding="utf-8"))
                    run_id = data.get("run_id", path.stem)
                    status = data.get("status", "unknown")
                    simulated = data.get("simulated", False)
                    mode = "SIM" if simulated else "HW"
                    self.history_list.insert("end", f"{mode} :: {status} :: {run_id}")
                except Exception:
                    self.history_list.insert("end", f"BAD :: {path.name}")

    def open_selected_artifact(self, event=None) -> None:
        selection = self.artifact_list.curselection()
        if not selection:
            return
        path = self.artifact_index[selection[0]]
        self._open_path_in_output(path)

    def open_selected_history(self, event=None) -> None:
        selection = self.history_list.curselection()
        if not selection:
            return
        path = self.run_history_index[selection[0]]
        self._open_path_in_output(path)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            self._update_badges(data.get("contracts", {}))
        except Exception:
            pass

    def _open_path_in_output(self, path: Path) -> None:
        try:
            text = path.read_text(encoding="utf-8")
            self._set_text(self.output_text, text)
            self.status_var.set(f"Opened: {path.name}")
        except Exception as exc:
            messagebox.showerror("Open failed", str(exc))
            self.status_var.set("Open failed.")


def launch() -> None:
    app = ChemiframeApp()
    app.mainloop()

