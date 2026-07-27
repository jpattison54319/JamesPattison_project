"""Application shell for the FitLens desktop UI."""

from __future__ import annotations

from pathlib import Path

import customtkinter as ctk
import engine

from .desktop_dashboard import DashboardView
from .desktop_onboarding import OnboardingView
from .desktop_theme import COLORS


class DashboardApp(ctk.CTk):
    """Main window for the dashboard and import screens."""

    def __init__(self, db_path: Path):
        """Builds the main window and chooses the right first screen. Returns None."""
        super().__init__()
        self.db_path = Path(db_path)
        self.main_view = None

        self.title("FitLens")
        self.geometry("1240x860")
        self.minsize(900, 620)
        self.configure(fg_color=COLORS["background"])
        self.protocol("WM_DELETE_WINDOW", self.destroy)

        self._build_shell()
        self._show_start_view()

    def _build_shell(self):
        """Builds the sidebar and main content area used by both app flows. Returns None."""
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        sidebar = ctk.CTkFrame(
            self,
            width=224,
            corner_radius=0,
            fg_color=COLORS["sidebar"],
        )
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        sidebar.grid_rowconfigure(4, weight=1)

        brand = ctk.CTkFrame(sidebar, fg_color="transparent")
        brand.grid(row=0, column=0, sticky="ew", padx=24, pady=(28, 34))
        ctk.CTkLabel(
            brand,
            text="FITLENS",
            text_color=COLORS["accent"],
            font=ctk.CTkFont(size=21, weight="bold"),
            anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            brand,
            text="Personal training intelligence",
            text_color=COLORS["muted"],
            font=ctk.CTkFont(size=11),
            anchor="w",
        ).pack(anchor="w", pady=(4, 0))

        self.sidebar_buttons = {}
        self._add_sidebar_button(
            sidebar, "dashboard", "Dashboard", 1, self.show_dashboard
        )
        self._add_sidebar_button(sidebar, "upload", "Upload", 2, self.show_import)

        self.sidebar_status = ctk.CTkLabel(
            sidebar,
            text="Loading data...",
            text_color=COLORS["muted"],
            font=ctk.CTkFont(size=11),
            justify="left",
            anchor="sw",
            wraplength=170,
        )
        self.sidebar_status.grid(row=3, column=0, sticky="sw", padx=24, pady=(22, 28))

        self.sidebar_help = ctk.CTkLabel(
            sidebar,
            text="",
            text_color=COLORS["muted"],
            font=ctk.CTkFont(size=11),
            justify="left",
            anchor="nw",
        )
        self.sidebar_help.grid(row=5, column=0, sticky="sw", padx=24, pady=(0, 28))

        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.grid(
            row=0, column=1, sticky="nsew", padx=(28, 34), pady=(26, 28)
        )
        self.main_area.grid_rowconfigure(0, weight=1)
        self.main_area.grid_columnconfigure(0, weight=1)

    def _show_start_view(self):
        """Start on the dashboard. It handles its own empty state."""
        self.show_dashboard()

    def _add_sidebar_button(self, parent, key, label, row, command):
        """Add one sidebar button."""
        button = ctk.CTkButton(
            parent,
            text=f"  {label}",
            height=38,
            corner_radius=9,
            fg_color="transparent",
            hover_color=COLORS["card_border"],
            text_color=COLORS["muted"],
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
            command=command,
        )
        button.grid(row=row, column=0, sticky="ew", padx=14, pady=(0, 4))
        self.sidebar_buttons[key] = button

    def _set_active_section(self, key):
        """Highlight the selected sidebar button."""
        for section, button in self.sidebar_buttons.items():
            active = section == key
            button.configure(
                fg_color=COLORS["accent_dark"] if active else "transparent",
                text_color=COLORS["text"] if active else COLORS["muted"],
            )

    def _set_navigation_enabled(self, enabled: bool):
        """Keep navigation still while an upload is running."""
        state = "normal" if enabled else "disabled"
        for button in self.sidebar_buttons.values():
            button.configure(state=state)

    def _clear_main_view(self):
        """Removes the currently displayed main view if there is one. Returns None."""
        if self.main_view is not None:
            self.main_view.destroy()
        self.main_view = None

    def show_import(self):
        """Show the upload screen for a first or later export pair."""
        snapshot = engine.db_snapshot(str(self.db_path)) or {}
        self._show_import_view(
            existing_user=bool(snapshot),
            default_timezone=snapshot.get("tz_name"),
        )

    def _show_import_view(
        self, existing_user: bool, default_timezone: str | None = None
    ):
        """Show the right upload version for this user."""
        self._clear_main_view()
        self._set_active_section("upload")
        if existing_user:
            self.sidebar_status.configure(text="Ready to reconcile new uploads")
            self.sidebar_help.configure(
                text=(
                    "Upload workflow\n\nChoose the newest Apple Health\n"
                    "XML and Hevy CSV exports.\n\nExisting data stays local."
                )
            )
        else:
            self.sidebar_status.configure(text="Ready for your first upload")
            self.sidebar_help.configure(
                text=(
                    "Upload workflow\n\nSelect your Apple Health\n"
                    "XML export and Hevy CSV.\n\nYour data stays local."
                )
            )
        self.main_view = OnboardingView(
            self.main_area,
            self.db_path,
            on_complete=self._onboarding_complete,
            existing_user=existing_user,
            default_timezone=default_timezone,
            on_cancel=self.show_dashboard if existing_user else None,
            on_view_dashboard=self.show_dashboard,
            on_upload_again=self.show_import,
            on_import_state_changed=self._set_navigation_enabled,
        )
        self.main_view.grid(row=0, column=0, sticky="nsew")

    def show_dashboard(self):
        """Builds and displays the monthly coaching dashboard. Returns None."""
        self._clear_main_view()
        self._set_active_section("dashboard")
        snapshot = engine.db_snapshot(str(self.db_path))
        if snapshot:
            self._update_sidebar_from_snapshot()
        else:
            self.sidebar_status.configure(text="No imported data yet")
        self.sidebar_help.configure(
            text=(
                "Upload workflow\n\nUse Upload to add your newest\n"
                "Apple Health and Hevy exports.\n\nThe CLI is also available:\n"
                "python fitlens.py"
            )
        )
        self.main_view = DashboardView(
            self.main_area,
            self.db_path,
            on_import_requested=self.show_import,
            on_data_loaded=self._update_sidebar,
        )
        self.main_view.grid(row=0, column=0, sticky="nsew")

    def _onboarding_complete(self, report):
        """Refresh the sidebar while the upload confirmation stays on screen."""
        self._update_sidebar_from_snapshot()

    def _update_sidebar_from_snapshot(self):
        """Refresh sidebar totals without rebuilding the dashboard."""
        self._set_sidebar_status(engine.db_snapshot(str(self.db_path)))

    def _update_sidebar(self, data):
        """Update sidebar totals after the dashboard loads."""
        self._set_sidebar_status(data.database)

    def _set_sidebar_status(self, snapshot):
        """Show the current import totals in the sidebar."""
        if not snapshot:
            self.sidebar_status.configure(text="No imported data yet")
            return

        self.sidebar_status.configure(
            text=(
                f"{snapshot['workouts']:,} workouts\n"
                f"{snapshot['days']:,} health days\n"
                f"{snapshot['nights']:,} sleep nights"
            )
        )
