# Task Ticker v9 - Task Dependencies and Sequencing

Task Ticker is a Python-based task management application built using the `tkinter` library. It allows users to create, manage, and organize tasks with features such as task dependencies, sequencing, grouping, and sorting. This README provides an overview of the script's functionality and how it works.

---

## Features

1. **Task Management**:
   - Add tasks with details such as due date, group, sequence, and dependencies.
   - Delete tasks or toggle their status between "Pending" and "Done".

2. **Task Dependencies**:
   - Tasks can depend on other tasks, ensuring that dependent tasks cannot be marked as "Done" until their parent tasks are completed.

3. **Task Sequencing**:
   - Assign sequence numbers to tasks for ordering purposes.

4. **Grouping**:
   - Organize tasks into groups (e.g., "Personal", "Work").
   - Filter tasks by group.

5. **Sorting**:
   - Sort tasks by due date, creation date, priority, or sequence.

6. **Persistence**:
   - Tasks and settings are saved to JSON files (`tasks.json` and `settings.json`) for persistence across sessions.
   - Automatic backup of tasks to tasks_backup.json.

7. **User Interface**:
   - A graphical interface built with `tkinter` for easy interaction.
   - Dropdown menus, listboxes, and input fields for managing tasks.

8. **Logging**:
   - Logs application events to task_ticker.log for debugging and tracking.

---

## File Structure

- **`tasks.json`**: Stores the list of tasks.
- **`tasks_backup.json`**: Backup of the tasks file.
- **`settings.json`**: Stores user settings such as sorting preferences.
- **`task_ticker.log`**: Logs application events.

---

## How It Works

### Initialization

The `TaskTickerApp` class initializes the application:

- Sets up the main window with a fixed size and title.
- Loads tasks and settings from their respective JSON files.
- Creates the user interface widgets.

### User Interface

The UI consists of:

1. **Control Panel**:
   - Dropdowns for filtering tasks by status and group.
   - Sorting options and a "Sort Now" button.

2. **Task Entry Panel**:
   - Input fields for task name, due date, sequence, and group.
   - A dropdown for selecting task dependencies.
   - An "Add Task" button.

3. **Task List**:
   - Displays tasks in a listbox with details such as sequence, status, group, and due date.
   - Tasks with unmet dependencies are marked with a "⛔" symbol.

4. **Action Buttons**:
   - Buttons for deleting tasks and toggling their status.

### Core Methods

- **`add_task`**: Adds a new task to the list and saves it to the JSON file.
- **`delete_task`**: Deletes the selected task.
- **`toggle_task_status`**: Toggles the status of the selected task, ensuring dependencies are met.
- **`sort_and_render`**: Sorts tasks based on the selected key and updates the task list display.
- **`render_task_list`**: Displays tasks in the listbox, applying filters and dependency checks.
- **`update_group_filter_options`**: Updates the group filter dropdown based on existing task groups.
- **`update_dependency_dropdown`**: Updates the dependency dropdown with available tasks.
- **`save_tasks_to_file`**: Saves tasks to tasks.json and creates a backup.
- **`load_tasks_from_file`**: Loads tasks from tasks.json.

### Dependency Management

- Tasks can depend on other tasks, and the application ensures that dependent tasks cannot be marked as "Done" until their parent tasks are completed.
- Dependency conflicts (e.g., circular dependencies or invalid due dates) are handled with warnings.

---

## How to Run

1. Install the required libraries:
   ```bash
   pip install tkcalendar
   ```

2. Run the script:
   ```bash
   python task_ticker.py
   ```

3. Use the graphical interface to manage your tasks.

---

## Logging

The application logs events such as task additions, deletions, and errors to task_ticker.log. This helps in debugging and tracking user actions.

---

## Future Improvements

- Add support for recurring tasks.
- Implement advanced filtering options.
- Enhance the UI for better usability.

---

This script is a robust task management tool designed for personal productivity. Feel free to customize it to suit your needs!