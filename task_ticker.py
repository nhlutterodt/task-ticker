'''
Task Ticker v10 - Enhanced Configuration, Modularity, and Error Handling
Author: Neils Haldane-Lutterodt
'''

import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
import json
import os
from uuid import uuid4
from datetime import datetime
import shutil
import logging
import traceback
from typing import Dict, List, Optional, Any

# ---------------------------
# CONFIGURATION
# ---------------------------
class Config:
    """Centralized configuration management"""
    PATHS = {
        "TASKS": "tasks.json",
        "BACKUP": "tasks_backup.json",
        "SETTINGS": "settings.json",
        "LOG": "task_ticker.log"
    }

    DEFAULT_SETTINGS = {
        "auto_sort": False,
        "default_sort": "due_date",
        "default_group": "Personal",
        "window_size": "600x680"
    }

    UI_STRINGS = {
        "WINDOW_TITLE": "Task Ticker 📝",
        "ERROR_NO_SELECTION": "Please select a task.",
        "ERROR_EMPTY_INPUT": "Please enter a task.",
        "ERROR_DEPENDENCY_SELF": "A task cannot depend on itself.",
        "ERROR_DEPENDENCY_UNMET": "This task depends on '{}' which is not yet done.",
        "ERROR_DUE_DATE": "Dependent task has an earlier due date than its parent.",
        "ERROR_LOAD": "Error loading {}: {}",
    }

# ---------------------------
# LOGGING SETUP
# ---------------------------
class LoggerSetup:
    """Centralized logging configuration"""
    @staticmethod
    def setup_logger():
        logger = logging.getLogger('task_ticker')
        logger.setLevel(logging.INFO)
        
        # File handler
        file_handler = logging.FileHandler(Config.PATHS["LOG"])
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Clear existing handlers
        logger.handlers = []
        logger.addHandler(file_handler)
        
        return logger

logger = LoggerSetup.setup_logger()

# ---------------------------
# ERROR HANDLING
# ---------------------------
class ErrorHandler:
    """Centralized error handling"""
    @staticmethod
    def handle_error(error: Exception, context: str, show_message: bool = True) -> None:
        error_msg = f"{context}: {str(error)}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        if show_message:
            messagebox.showerror("Error", error_msg)

# ---------------------------
# FILE OPERATIONS
# ---------------------------
class FileManager:
    """Handles all file operations"""
    @staticmethod
    def load_json(filepath: str, default: Any = None) -> Any:
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    return json.load(f)
            return default
        except Exception as e:
            ErrorHandler.handle_error(e, f"Error loading {filepath}")
            return default

    @staticmethod
    def save_json(filepath: str, data: Any, create_backup: bool = False) -> bool:
        try:
            if create_backup and os.path.exists(filepath):
                shutil.copy(filepath, Config.PATHS["BACKUP"])
                logger.info(f"Backup created: {Config.PATHS['BACKUP']}")

            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)
            logger.info(f"Successfully saved to {filepath}")
            return True
        except Exception as e:
            ErrorHandler.handle_error(e, f"Error saving to {filepath}")
            return False

# ---------------------------
# TASK MANAGEMENT
# ---------------------------
class TaskManager:
    """Handles task operations and data management"""
    def __init__(self):
        self.tasks: List[Dict] = []
        self.visible_tasks: List[Dict] = []
        self.dependency_map: Dict[str, str] = {}

    def load_tasks(self) -> None:
        """Load tasks with error handling"""
        loaded_tasks = FileManager.load_json(Config.PATHS["TASKS"], default=[])
        if loaded_tasks is not None:
            self.tasks = loaded_tasks
            logger.info("Tasks loaded successfully")
        else:
            self.tasks = []
            logger.warning("Starting with empty task list")

    def save_tasks(self) -> None:
        """Save tasks with backup"""
        FileManager.save_json(Config.PATHS["TASKS"], self.tasks, create_backup=True)

    def add_task(self, task_data: Dict) -> bool:
        """Add a new task with validation"""
        try:
            task = {
                "id": str(uuid4()),
                "created_at": datetime.now().isoformat(),
                "status": "pending",
                **task_data
            }
            self.tasks.append(task)
            self.save_tasks()
            logger.info(f"Task added: {task['task']}")
            return True
        except Exception as e:
            ErrorHandler.handle_error(e, "Error adding task")
            return False

    def delete_task(self, task_id: str) -> bool:
        """Delete a task by ID"""
        try:
            self.tasks = [t for t in self.tasks if t["id"] != task_id]
            self.save_tasks()
            logger.info(f"Task deleted: {task_id}")
            return True
        except Exception as e:
            ErrorHandler.handle_error(e, "Error deleting task")
            return False

    def toggle_task_status(self, task_id: str) -> Optional[bool]:
        """Toggle task status with dependency check"""
        try:
            task = self.find_task_by_id(task_id)
            if not task:
                return None

            if task.get("depends_on"):
                dep = self.find_task_by_id(task["depends_on"])
                if dep and dep["status"] != "done":
                    return False

            task["status"] = "done" if task["status"] == "pending" else "pending"
            self.save_tasks()
            logger.info(f"Task status toggled: {task['task']}")
            return True
        except Exception as e:
            ErrorHandler.handle_error(e, "Error toggling task status")
            return None

    def find_task_by_id(self, task_id: str) -> Optional[Dict]:
        """Find a task by ID"""
        return next((t for t in self.tasks if t["id"] == task_id), None)

    def get_filtered_tasks(self, status: str, group: str) -> List[Dict]:
        """Get filtered tasks based on status and group"""
        filtered = self.tasks
        if status != "All":
            filtered = [t for t in filtered if t["status"].lower() == status.lower()]
        if group != "All Groups":
            filtered = [t for t in filtered if t["group"] == group]
        return filtered

    def sort_tasks(self, key: str) -> None:
        """Sort tasks by the specified key"""
        self.tasks.sort(key=lambda t: t.get(key) or ("9999-12-31" if key == "due_date" else 9999))

# ---------------------------
# UI COMPONENTS
# ---------------------------
class TaskTickerUI:
    """Handles UI creation and updates"""
    def __init__(self, root: tk.Tk, task_manager: TaskManager):
        self.root = root
        self.task_manager = task_manager
        self.setup_window()
        self.create_variables()
        self.create_widgets()

    def setup_window(self) -> None:
        """Initialize window properties"""
        self.root.title(Config.UI_STRINGS["WINDOW_TITLE"])
        self.root.geometry(Config.DEFAULT_SETTINGS["window_size"])
        self.root.resizable(False, False)

    def create_variables(self) -> None:
        """Initialize Tkinter variables"""
        self.filter_mode = tk.StringVar(value="All")
        self.group_filter = tk.StringVar(value="All Groups")
        self.group_entry_var = tk.StringVar(value=Config.DEFAULT_SETTINGS["default_group"])
        self.sort_key = tk.StringVar(value=Config.DEFAULT_SETTINGS["default_sort"])
        self.selected_dependency = tk.StringVar(value="None")
        self.sequence_input = tk.StringVar(value="1")

    def create_widgets(self) -> None:
        """Create all UI widgets"""
        self.create_control_frame()
        self.create_entry_frame()
        self.create_dependency_frame()
        self.create_list_frame()
        self.create_button_frame()

    def create_control_frame(self) -> None:
        """Create the control panel frame"""
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=(10, 0))

        # Status filter
        tk.Label(control_frame, text="Status:").grid(row=0, column=0, padx=5)
        status_menu = tk.OptionMenu(control_frame, self.filter_mode, 
                                  "All", "Pending", "Done", 
                                  command=self.on_filter_change)
        status_menu.grid(row=0, column=1)

        # Group filter
        tk.Label(control_frame, text="Group:").grid(row=0, column=2, padx=5)
        self.group_dropdown = tk.OptionMenu(control_frame, self.group_filter, 
                                          "All Groups", 
                                          command=self.on_filter_change)
        self.group_dropdown.grid(row=0, column=3)

        # Sort controls
        tk.Label(control_frame, text="Sort by:").grid(row=1, column=0, padx=5)
        sort_menu = tk.OptionMenu(control_frame, self.sort_key,
                                "due_date", "created_at", "priority", "sequence",
                                command=self.on_sort_change)
        sort_menu.grid(row=1, column=1)

        sort_btn = tk.Button(control_frame, text="Sort Now",
                           command=self.on_sort_change)
        sort_btn.grid(row=1, column=2, columnspan=2, pady=5)

    def create_entry_frame(self) -> None:
        """Create the task entry frame"""
        entry_frame = tk.Frame(self.root)
        entry_frame.pack(pady=10)

        self.task_input = tk.Entry(entry_frame, width=30)
        self.task_input.pack(side=tk.LEFT, padx=(10, 5))

        self.due_input = DateEntry(entry_frame, width=12,
                                 background='darkblue',
                                 foreground='white',
                                 borderwidth=2,
                                 date_pattern='yyyy-mm-dd')
        self.due_input.pack(side=tk.LEFT, padx=5)

        self.sequence_entry = tk.Entry(entry_frame, width=5,
                                     textvariable=self.sequence_input)
        self.sequence_entry.pack(side=tk.LEFT)

        self.group_input = tk.Entry(entry_frame, width=10,
                                  textvariable=self.group_entry_var)
        self.group_input.pack(side=tk.LEFT, padx=5)

        add_btn = tk.Button(entry_frame, text="Add Task",
                          command=self.on_add_task,
                          bg="#4CAF50", fg="white")
        add_btn.pack(side=tk.LEFT)

    def create_dependency_frame(self) -> None:
        """Create the dependency selection frame"""
        dep_frame = tk.Frame(self.root)
        dep_frame.pack()

        tk.Label(dep_frame, text="Depends On:").pack(side=tk.LEFT)
        self.dep_dropdown = tk.OptionMenu(dep_frame, self.selected_dependency, "None")
        self.dep_dropdown.pack(side=tk.LEFT)

    def create_list_frame(self) -> None:
        """Create the task list frame"""
        list_frame = tk.Frame(self.root)
        list_frame.pack(pady=10)

        self.task_listbox = tk.Listbox(list_frame, height=18, width=80)
        self.task_listbox.pack(side=tk.LEFT)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.task_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.task_listbox.yview)

    def create_button_frame(self) -> None:
        """Create the action buttons frame"""
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Delete Task",
                command=self.on_delete_task,
                bg="#f44336", fg="white").grid(row=0, column=0, padx=10)

        tk.Button(btn_frame, text="Toggle Done",
                command=self.on_toggle_status,
                bg="#2196F3", fg="white").grid(row=0, column=1, padx=10)

    def update_group_filter_options(self) -> None:
        """Update group filter dropdown options"""
        groups = sorted({t["group"] for t in self.task_manager.tasks})
        menu = self.group_dropdown["menu"]
        menu.delete(0, "end")
        menu.add_command(label="All Groups",
                        command=lambda: self.set_group_filter("All Groups"))
        for g in groups:
            menu.add_command(label=g,
                           command=lambda val=g: self.set_group_filter(val))

    def update_dependency_dropdown(self) -> None:
        """Update dependency selection dropdown"""
        self.task_manager.dependency_map.clear()
        menu = self.dep_dropdown["menu"]
        menu.delete(0, "end")
        menu.add_command(label="None",
                        command=lambda: self.selected_dependency.set("None"))
        for task in self.task_manager.tasks:
            label = f"{task['task']} [{task['group']}] (ID: {task['id'][:6]}...)"
            self.task_manager.dependency_map[label] = task["id"]
            menu.add_command(label=label,
                           command=lambda val=label: self.selected_dependency.set(val))

    def render_task_list(self) -> None:
        """Render the filtered task list"""
        self.task_listbox.delete(0, tk.END)
        self.task_manager.visible_tasks = self.task_manager.get_filtered_tasks(
            self.filter_mode.get(),
            self.group_filter.get()
        )
        for t in self.task_manager.visible_tasks:
            blocked = " ⛔" if t.get("depends_on") and \
                     self.task_manager.find_task_by_id(t["depends_on"])["status"] != "done" else ""
            seq = f"[{t.get('sequence', '?')}]"
            line = f"{seq} {'✔' if t['status']=='done' else ''} {t['task']} [{t['group']}] (Due: {t['due_date']}){blocked}"
            self.task_listbox.insert(tk.END, line)

    # Event Handlers
    def on_add_task(self) -> None:
        """Handle add task button click"""
        text = self.task_input.get().strip()
        if not text:
            messagebox.showwarning("Empty Input",
                                 Config.UI_STRINGS["ERROR_EMPTY_INPUT"])
            return

        group = self.group_input.get().strip() or "General"
        due_date = self.due_input.get_date().isoformat()
        sequence = int(self.sequence_input.get() or 1)
        dep_label = self.selected_dependency.get()
        depends_on = self.task_manager.dependency_map.get(dep_label) \
                    if dep_label != "None" else None

        if depends_on:
            parent = self.task_manager.find_task_by_id(depends_on)
            if parent and parent['due_date'] > due_date:
                messagebox.showwarning("Due Date Conflict",
                                     Config.UI_STRINGS["ERROR_DUE_DATE"])
                return

        task_data = {
            "task": text,
            "group": group.title(),
            "due_date": due_date,
            "priority": "normal",
            "sequence": sequence,
            "depends_on": depends_on
        }

        if self.task_manager.add_task(task_data):
            self.task_input.delete(0, tk.END)
            self.group_entry_var.set(group.title())
            self.sequence_input.set(str(sequence + 1))
            self.selected_dependency.set("None")
            self.update_ui()

    def on_delete_task(self) -> None:
        """Handle delete task button click"""
        try:
            idx = self.task_listbox.curselection()[0]
            task = self.task_manager.visible_tasks[idx]
            if self.task_manager.delete_task(task["id"]):
                self.update_ui()
        except IndexError:
            messagebox.showerror("No Selection",
                               Config.UI_STRINGS["ERROR_NO_SELECTION"])

    def on_toggle_status(self) -> None:
        """Handle toggle status button click"""
        try:
            idx = self.task_listbox.curselection()[0]
            task = self.task_manager.visible_tasks[idx]
            result = self.task_manager.toggle_task_status(task["id"])
            
            if result is False:  # Dependency not met
                dep = self.task_manager.find_task_by_id(task["depends_on"])
                messagebox.showwarning(
                    "Dependency Unmet",
                    Config.UI_STRINGS["ERROR_DEPENDENCY_UNMET"].format(dep['task'])
                )
            elif result is True:  # Successfully toggled
                self.update_ui()
        except IndexError:
            messagebox.showerror("No Selection",
                               Config.UI_STRINGS["ERROR_NO_SELECTION"])

    def on_filter_change(self, *args) -> None:
        """Handle filter change"""
        self.render_task_list()

    def on_sort_change(self, *args) -> None:
        """Handle sort change"""
        self.task_manager.sort_tasks(self.sort_key.get())
        self.render_task_list()

    def update_ui(self) -> None:
        """Update all UI elements"""
        self.update_group_filter_options()
        self.update_dependency_dropdown()
        self.on_sort_change()

# ---------------------------
# MAIN APPLICATION
# ---------------------------
class TaskTickerApp:
    """Main application class"""
    def __init__(self):
        self.root = tk.Tk()
        self.task_manager = TaskManager()
        self.ui = None
        self.initialize_app()

    def initialize_app(self) -> None:
        """Initialize the application with proper error handling"""
        try:
            logger.info("Initializing Task Ticker application")
            self.task_manager.load_tasks()
            self.ui = TaskTickerUI(self.root, self.task_manager)
            self.ui.update_ui()
            logger.info("Application initialized successfully")
        except Exception as e:
            ErrorHandler.handle_error(e, "Error initializing application")
            self.root.destroy()
            return

    def run(self) -> None:
        """Start the application"""
        try:
            self.root.mainloop()
        except Exception as e:
            ErrorHandler.handle_error(e, "Error in main loop")
        finally:
            logger.info("Application closed")
            logging.shutdown()

if __name__ == "__main__":
    app = TaskTickerApp()
    app.run()
