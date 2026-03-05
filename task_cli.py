import os
import json
from datetime import datetime
import sys

# ===== CONSTANTS =====
TASKS_FILE = "task.json"
DEFAULT_FILE = "task.json"


# ===== ENHANCEMENT 1: COLOR OUTPUT (ANSI Codes - No Libraries Needed) =====
# ANSI escape codes are special character sequences that terminals interpret as formatting instructions
# They work in most modern terminals (PowerShell, VS Code Terminal, Mac/Linux Terminal)
# Format: \033[<code>m where <code> is the color/style number
class Colors:
    GREEN = "\033[92m"    # Used for: done status, low priority
    YELLOW = "\033[93m"   # Used for: in-progress status, medium priority
    RED = "\033[91m"      # Used for: todo status, high priority
    BLUE = "\033[94m"     # Used for: info messages
    BOLD = "\033[1m"      # Used for: headers
    RESET = "\033[0m"     # Resets all formatting back to default


# ENHANCEMENT 1 (continued): Colorize task status text
# Takes a status string and wraps it in the appropriate ANSI color code
def colorize_status(status):
    if status == "done":
        return f"{Colors.GREEN}{status}{Colors.RESET}"
    elif status == "in-progress":
        return f"{Colors.YELLOW}{status}{Colors.RESET}"
    elif status == "todo":
        return f"{Colors.RED}{status}{Colors.RESET}"
    return status


# ===== ENHANCEMENT 5: PRIORITY LEVELS =====
# Colorize priority text similar to status
# High = Red (urgent), Medium = Yellow (normal), Low = Green (not urgent)
def colorize_priority(priority):
    if priority == "high":
        return f"{Colors.RED}{priority}{Colors.RESET}"
    elif priority == "medium":
        return f"{Colors.YELLOW}{priority}{Colors.RESET}"
    elif priority == "low":
        return f"{Colors.GREEN}{priority}{Colors.RESET}"
    return priority


# ===== ENHANCEMENT 3: SHOW TIMESTAMPS IN LIST =====
# Converts ISO format datetime string to a short readable format
# Example: "2026-03-05T14:30:00.000000" → "2026-03-05 14:30"
def format_datetime(iso_string):
    try:
        dt = datetime.fromisoformat(iso_string)
        return dt.strftime("%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        return "N/A"


# ===== ENHANCEMENT 9: MULTIPLE TASK LISTS (PROJECTS) =====
# Returns the correct JSON filename based on the project name
# If no project is specified, uses the default "task.json"
# Example: project="work" → "work.json", project=None → "task.json"
def get_tasks_file(project=None):
    if project:
        return f"{project}.json"
    return DEFAULT_FILE


# ===== CORE FUNCTION: LOAD TASKS =====
# Reads tasks from the JSON file and returns them as a Python list
# Enhancement 9: Added 'project' parameter to support multiple task lists
def load_tasks(project=None):
    # Enhancement 9: Get the correct file based on project
    tasks_file = get_tasks_file(project)

    # checks if a file exists before reading, if available we can read it
    if os.path.exists(tasks_file):
        try:
            # opens the file in read mode ("r")
            # with ... as file: is a safe way to open files - it automatically closes the file when done
            with open(tasks_file, "r") as file:
                # reads the JSON content and converts it to a python list
                return json.load(file)
        except json.JSONDecodeError:
            # file exists but contains invalid JSON
            print(f"Error: {tasks_file} is corrupted. Starting with empty list.")
            return []
        except IOError:
            # problem reading the file
            print(f"Error: Could not read {tasks_file}.")
            return []
    # return an empty list when file does not exist
    return []


# ===== CORE FUNCTION: SAVE TASKS =====
# Writes the tasks list to the JSON file
# Enhancement 9: Added 'project' parameter to support multiple task lists
def save_tasks(tasks, project=None):
    # Enhancement 9: Get the correct file based on project
    tasks_file = get_tasks_file(project)

    try:
        # open JSON file in write mode
        with open(tasks_file, "w") as file:
            # json.dump() converts a python object to JSON and writes it to a file
            # indent=4 adds 4 spaces of indentation for human readable format
            json.dump(tasks, file, indent=4)
    except IOError:
        print("Error: Could not save tasks to file.")
    except TypeError as e:
        print(f"Error: Invalid data format. {e}")


# ===== CORE FUNCTION: ADD TASKS =====
# Creates a new task with description, status, priority, and timestamps
# Enhancement 5: Added 'priority' parameter (high, medium, low)
# Enhancement 9: Added 'project' parameter for multiple task lists
def add_tasks(description, priority="medium", project=None):
    # input validation - catches empty strings or None
    if not description:
        print("Error: Task description cannot be empty.")
        return

    # ensures input is a string
    if not isinstance(description, str):
        print("Error: Task description must be text.")
        return

    # remove extra whitespace, leading/trailing spaces
    description = description.strip()

    # catches strings that were only spaces
    if len(description) == 0:
        print("Error: Task description cannot be empty.")
        return

    # Enhancement 5: Validate priority level
    valid_priorities = ["high", "medium", "low"]
    priority = priority.lower().strip()

    if priority not in valid_priorities:
        print(f"Error: Invalid priority '{priority}'.")
        print(f"Valid options: {', '.join(valid_priorities)}")
        return

    # before adding new task, loading the current tasks from the file
    tasks = load_tasks(project)

    # generate unique ID
    if len(tasks) == 0:
        new_id = 1
    else:
        # finding the highest ID in the list and add 1 to get the next available ID
        new_id = max(task["id"] for task in tasks) + 1

    # get current date and time, convert to string format
    # JSON doesn't support python datetime objects directly
    # ISO format is a standard, readable string format
    current_time = datetime.now().isoformat()

    # create the new task dictionary
    # Enhancement 5: Added "priority" field
    new_task = {
        "id": new_id,
        "description": description,
        "status": "todo",
        "priority": priority,
        "createdAt": current_time,
        "updatedAt": current_time
    }

    # add to list and save
    tasks.append(new_task)
    save_tasks(tasks, project)
    print(f"Task added successfully (ID: {new_id}) [Priority: {priority}]")


# ===== CORE FUNCTION: UPDATE TASKS =====
# Updates the description of an existing task by ID
# Enhancement 9: Added 'project' parameter for multiple task lists
def update_tasks(task_id, new_description, project=None):
    # input validation - validate task_id is a number
    if not isinstance(task_id, int):
        print("Error: Task ID must be a number.")
        return

    # ensures ID is positive
    if task_id <= 0:
        print("Error: Task ID must be positive number.")
        return

    # validate new_description
    if not new_description:
        print("Error: New description cannot be empty.")
        return

    # remove extra whitespace
    new_description = new_description.strip()

    # catches empty or None
    if len(new_description) == 0:
        print("Error: New description cannot be empty.")
        return

    # load existing tasks
    tasks = load_tasks(project)

    # flag to track if task was found, initializing flag as False
    task_found = False

    # search for the task
    for task in tasks:
        if task["id"] == task_id:
            # update the old description with new one
            task["description"] = new_description

            # update the timestamp only in "updatedAt" field
            task["updatedAt"] = datetime.now().isoformat()

            # set to True when task is found
            task_found = True
            break  # exit the loop immediately

    # check the flag after the loop
    if task_found:
        save_tasks(tasks, project)
        print(f"Task {task_id} updated successfully.")
    else:
        print(f"Error: Task with ID {task_id} not found.")


# ===== CORE FUNCTION: DELETE TASKS =====
# Removes a task from the list by ID
# Enhancement 9: Added 'project' parameter for multiple task lists
def delete_tasks(task_id, project=None):
    # validating the task_id
    if not isinstance(task_id, int):
        print("Error: Task ID must be a number.")
        return

    # validate ID is positive
    if task_id <= 0:
        print("Error: Task ID must be a positive number.")
        return

    # load existing tasks
    tasks = load_tasks(project)

    # check if any tasks exist
    if len(tasks) == 0:
        print("Error: No tasks found. Nothing to delete.")
        return

    # search for the task
    for task in tasks:
        if task["id"] == task_id:
            tasks.remove(task)

            # save to file
            save_tasks(tasks, project)

            # print confirmation
            print(f"Task {task_id} deleted successfully.")

            # exit the function after deleting
            return

    # handle task not found
    print(f"Error: Task with ID {task_id} not found.")


# ===== CORE FUNCTION: MARK IN PROGRESS =====
# Changes a task's status to "in-progress"
# Enhancement 9: Added 'project' parameter for multiple task lists
def mark_in_progress(task_id, project=None):
    # Validate task_id
    if not isinstance(task_id, int):
        print("Error: Task ID must be a number.")
        return

    # check ID must be positive
    if task_id <= 0:
        print("Error: Task ID must be a positive number.")
        return

    # Load existing tasks
    tasks = load_tasks(project)

    # Check if any tasks exist
    if len(tasks) == 0:
        print("Error: No tasks found.")
        return

    # Search for the task
    for task in tasks:
        if task["id"] == task_id:
            # Check if already in progress
            if task["status"] == "in-progress":
                print(f"Task {task_id} is already in progress.")
                return

            # Update the task
            task["status"] = "in-progress"
            task["updatedAt"] = datetime.now().isoformat()

            # Save changes
            save_tasks(tasks, project)

            # Confirmation
            print(f"Task {task_id} marked as in progress.")
            return

    # Task not found
    print(f"Error: Task with ID {task_id} not found.")


# ===== CORE FUNCTION: MARK DONE =====
# Changes a task's status to "done"
# Enhancement 9: Added 'project' parameter for multiple task lists
def mark_done(task_id, project=None):
    # validate task_id
    if not isinstance(task_id, int):
        print("Error: Task ID must be a number.")
        return

    # validate task_id is positive number
    if task_id <= 0:
        print("Error: Task ID must be positive number.")
        return

    # loading existing tasks
    tasks = load_tasks(project)

    # check if any task exist
    if len(tasks) == 0:
        print("Error: No tasks found.")
        return

    # search for the task
    for task in tasks:
        if task["id"] == task_id:
            # update status
            task["status"] = "done"

            # update the timestamp
            task["updatedAt"] = datetime.now().isoformat()

            # save changes
            save_tasks(tasks, project)

            # confirmation
            print(f"Task {task_id} marked as done.")
            return

    # task not found
    print(f"Error: Task with ID {task_id} not found.")


# ===== ENHANCEMENT 6: SORT TASKS =====
# Sorts the task list by different criteria
# sort_by options: "id", "status", "priority", "date"
# Returns the sorted list (does not modify the file)
def sort_tasks(tasks, sort_by="id"):
    if sort_by == "id":
        # Sort by task ID (ascending: 1, 2, 3...)
        tasks.sort(key=lambda task: task["id"])

    elif sort_by == "status":
        # Custom order: in-progress first (active work), then todo, then done
        status_order = {"in-progress": 0, "todo": 1, "done": 2}
        tasks.sort(key=lambda task: status_order.get(task["status"], 3))

    elif sort_by == "priority":
        # Custom order: high first (most urgent), then medium, then low
        priority_order = {"high": 0, "medium": 1, "low": 2}
        tasks.sort(key=lambda task: priority_order.get(task.get("priority", "medium"), 3))

    elif sort_by == "date":
        # Sort by creation date (newest first)
        tasks.sort(key=lambda task: task.get("createdAt", ""), reverse=True)

    else:
        print(f"Error: Invalid sort option '{sort_by}'.")
        print("Valid options: id, status, priority, date")

    return tasks


# ===== ENHANCEMENT 2: TASK COUNT PER STATUS =====
# Displays a colored summary showing how many tasks are in each status
# Always shows counts for ALL tasks (ignores any active filter)
def print_status_summary(tasks):
    todo_count = 0
    in_progress_count = 0
    done_count = 0

    for task in tasks:
        if task["status"] == "todo":
            todo_count += 1
        elif task["status"] == "in-progress":
            in_progress_count += 1
        elif task["status"] == "done":
            done_count += 1

    # Display colored summary line
    print(
        f"\n  {Colors.RED}{todo_count} todo{Colors.RESET}, "
        f"{Colors.YELLOW}{in_progress_count} in-progress{Colors.RESET}, "
        f"{Colors.GREEN}{done_count} done{Colors.RESET}"
    )


# ===== CORE FUNCTION: LIST TASKS =====
# Displays tasks in a formatted table with colors
# Enhancement 1: Colored status text
# Enhancement 2: Status summary at the bottom
# Enhancement 3: Created/Updated timestamps in the table
# Enhancement 5: Priority column with colors
# Enhancement 6: Sort support (sort_by parameter)
# Enhancement 9: Project support
def list_tasks(status_filter=None, sort_by="id", project=None):
    # valid status values
    valid_statuses = ["todo", "in-progress", "done"]

    # validate the status filter if provided
    if status_filter is not None:
        if status_filter not in valid_statuses:
            print(f"Error: Invalid status '{status_filter}'.")
            print(f"Valid options: {', '.join(valid_statuses)}")
            return

    # loading existing tasks
    tasks = load_tasks(project)

    # check if any task exist
    if len(tasks) == 0:
        print("No tasks found. Add a task to get started!")
        return

    # store all tasks for the summary before filtering
    all_tasks = tasks[:]

    # filter tasks if a status filter is provided
    if status_filter is not None:
        tasks = [task for task in tasks if task["status"] == status_filter]

    # check if any tasks match the filter
    if len(tasks) == 0:
        print(f"No tasks found with status '{status_filter}'.")
        return

    # Enhancement 6: Sort tasks before displaying
    tasks = sort_tasks(tasks, sort_by)

    # Enhancement 3 & 5: Updated header with Priority, Created, Updated columns
    print("\n" + "=" * 95)
    print(f"  {'ID':<5} {'Status':<15} {'Priority':<10} {'Description':<25} {'Created':<18} {'Updated':<18}")
    print("=" * 95)

    # display each task
    for task in tasks:
        task_id = task['id']
        status = task['status']
        description = task['description']

        # Enhancement 5: Get priority (default to "medium" for old tasks without priority)
        priority = task.get('priority', 'medium')

        # Enhancement 3: Get formatted timestamps
        created = format_datetime(task.get('createdAt', ''))
        updated = format_datetime(task.get('updatedAt', ''))

        # truncate long descriptions to keep table aligned
        if len(description) > 22:
            description = description[:22] + "..."

        # Enhancement 1: Colorize status and priority
        colored_status = colorize_status(status)
        colored_priority = colorize_priority(priority)

        # Print the task row
        # Note: colored strings have hidden ANSI characters, so we use extra width
        # colored_status uses <24 instead of <15 (9 extra chars for ANSI codes)
        # colored_priority uses <19 instead of <10 (9 extra chars for ANSI codes)
        print(f"  {task_id:<5} {colored_status:<24} {colored_priority:<19} {description:<25} {created:<18} {updated:<18}")

    print("=" * 95)
    print(f"  Total: {len(tasks)} task(s)")

    # Enhancement 2: Show status summary for ALL tasks (not just filtered)
    print_status_summary(all_tasks)


# ===== ENHANCEMENT 4: SEARCH TASKS =====
# Searches task descriptions for a keyword (case-insensitive)
# Displays matching tasks in the same formatted table as list_tasks
# Enhancement 9: Added 'project' parameter for multiple task lists
def search_tasks(keyword, project=None):
    # Validate keyword
    if not keyword or len(keyword.strip()) == 0:
        print("Error: Please provide a search keyword.")
        return

    # Normalize keyword: remove whitespace and convert to lowercase for case-insensitive search
    keyword = keyword.strip().lower()

    # Load tasks
    tasks = load_tasks(project)

    if len(tasks) == 0:
        print("No tasks found.")
        return

    # Search - check if keyword appears anywhere in the description (case-insensitive)
    matched_tasks = []
    for task in tasks:
        if keyword in task["description"].lower():
            matched_tasks.append(task)

    # Display results
    if len(matched_tasks) == 0:
        print(f"No tasks found matching '{keyword}'.")
        return

    print(f"\n  Found {len(matched_tasks)} task(s) matching '{keyword}':\n")
    print("=" * 95)
    print(f"  {'ID':<5} {'Status':<15} {'Priority':<10} {'Description':<25} {'Created':<18} {'Updated':<18}")
    print("=" * 95)

    for task in matched_tasks:
        task_id = task['id']
        status = task['status']
        description = task['description']
        priority = task.get('priority', 'medium')
        created = format_datetime(task.get('createdAt', ''))
        updated = format_datetime(task.get('updatedAt', ''))

        if len(description) > 22:
            description = description[:22] + "..."

        # Enhancement 1: Colorize status and priority
        colored_status = colorize_status(status)
        colored_priority = colorize_priority(priority)

        print(f"  {task_id:<5} {colored_status:<24} {colored_priority:<19} {description:<25} {created:<18} {updated:<18}")

    print("=" * 95)


# ===== ENHANCEMENT 7: EXPORT TO CSV =====
# Exports all tasks to a CSV file that can be opened in Excel or Google Sheets
# CSV (Comma-Separated Values) is a simple text format for tabular data
# Enhancement 9: Added 'project' parameter for multiple task lists
def export_to_csv(project=None):
    tasks = load_tasks(project)

    if len(tasks) == 0:
        print("No tasks to export.")
        return

    # Create filename (if project is specified, include it in the name)
    if project:
        filename = f"{project}_tasks_export.csv"
    else:
        filename = "tasks_export.csv"

    try:
        with open(filename, "w") as file:
            # Write header row (column names)
            file.write("ID,Description,Status,Priority,Created At,Updated At\n")

            # Write each task as a row
            for task in tasks:
                task_id = task["id"]
                # Wrap description in quotes in case it contains commas
                # Replace any existing quotes with double quotes (CSV standard for escaping)
                description = '"' + task["description"].replace('"', '""') + '"'
                status = task["status"]
                priority = task.get("priority", "medium")
                created = task.get("createdAt", "")
                updated = task.get("updatedAt", "")

                file.write(f"{task_id},{description},{status},{priority},{created},{updated}\n")

        print(f"Tasks exported successfully to '{filename}'")
        print(f"Total: {len(tasks)} task(s) exported.")

    except IOError:
        print("Error: Could not write to file.")


# ===== ENHANCEMENT 8: BACKUP & RESTORE =====
# backup_tasks(): Creates a timestamped backup copy of the current tasks file
# Example backup filename: tasks_backup_20260305_143000.json
# Enhancement 9: Added 'project' parameter for multiple task lists
def backup_tasks(project=None):
    tasks = load_tasks(project)

    if len(tasks) == 0:
        print("No tasks to backup.")
        return

    # Create backup filename with timestamp so each backup is unique
    # Format: tasks_backup_YYYYMMDD_HHMMSS.json
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if project:
        backup_file = f"{project}_backup_{timestamp}.json"
    else:
        backup_file = f"tasks_backup_{timestamp}.json"

    try:
        with open(backup_file, "w") as file:
            json.dump(tasks, file, indent=4)
        print(f"Backup created successfully: {backup_file}")
        print(f"Total: {len(tasks)} task(s) backed up.")
    except IOError:
        print("Error: Could not create backup file.")


# restore_tasks(): Restores tasks from a previously created backup file
# Completely replaces current tasks with the backup data
# Enhancement 9: Added 'project' parameter for multiple task lists
def restore_tasks(backup_file, project=None):
    # Check if backup file exists
    if not os.path.exists(backup_file):
        print(f"Error: Backup file '{backup_file}' not found.")
        return

    try:
        # Read the backup file
        with open(backup_file, "r") as file:
            backup_data = json.load(file)

        # Validate it's a list (tasks should always be stored as a list)
        if not isinstance(backup_data, list):
            print("Error: Invalid backup file format.")
            return

        # Save the backup data as current tasks (overwrites existing tasks)
        save_tasks(backup_data, project)
        print(f"Tasks restored successfully from '{backup_file}'")
        print(f"Total: {len(backup_data)} task(s) restored.")

    except json.JSONDecodeError:
        print("Error: Backup file contains invalid JSON.")
    except IOError:
        print("Error: Could not read backup file.")


# ===== MAIN FUNCTION: CLI COMMAND ROUTING =====
# Parses command line arguments and routes to the correct function
# Handles all commands: add, update, delete, mark-in-progress, mark-done,
# list, search, export, backup, restore
# Enhancement 9: Handles --project flag for all commands
def main():
    if len(sys.argv) < 2:
        # Show usage instructions when no command is provided
        print("Error: No command provided.")
        print("")
        print("Usage: python task_cli.py <command> [arguments] [--project <name>]")
        print("")
        print("Available commands:")
        print("  add <description> [priority]       - Add a new task (priority: high/medium/low)")
        print("  update <id> <description>          - Update a task")
        print("  delete <id>                        - Delete a task")
        print("  mark-in-progress <id>              - Mark task as in progress")
        print("  mark-done <id>                     - Mark task as done")
        print("  list                               - List all tasks")
        print("  list <status>                      - List tasks by status (todo, in-progress, done)")
        print("  list [status] sort:<field>          - List sorted (id, status, priority, date)")
        print("  search <keyword>                   - Search tasks by keyword")
        print("  export                             - Export tasks to CSV")
        print("  backup                             - Create a backup of tasks")
        print("  restore <filename>                 - Restore tasks from backup")
        print("")
        print("Options:")
        print("  --project <name>                   - Use a specific project file")
        return

    # ===== ENHANCEMENT 9: Parse --project flag =====
    # Look for --project anywhere in the arguments
    # Remove it from the args list so it doesn't interfere with command parsing
    project = None
    args = sys.argv[:]  # create a copy of arguments

    for i in range(len(args)):
        if args[i] == "--project" and i + 1 < len(args):
            project = args[i + 1]   # store the project name
            args.pop(i)             # remove "--project"
            args.pop(i)             # remove the project name value
            break

    # Check if we still have a command after removing --project
    if len(args) < 2:
        print("Error: No command provided.")
        return

    # Get the command from arguments
    command = args[1].lower()

    # ===== COMMAND: ADD =====
    if command == "add":
        if len(args) < 3:
            print("Error: Please provide a task description.")
            print('Usage: python task_cli.py add "Task description" [priority]')
            return
        # Enhancement 5: Check if priority is provided as 3rd argument
        priority = args[3] if len(args) > 3 else "medium"
        add_tasks(args[2], priority, project)

    # ===== COMMAND: UPDATE =====
    elif command == "update":
        if len(args) < 4:
            print("Error: Please provide task ID and new description.")
            print('Usage: python task_cli.py update <id> "New description"')
            return
        try:
            task_id = int(args[2])
        except ValueError:
            print("Error: Task ID must be a number.")
            return
        update_tasks(task_id, args[3], project)

    # ===== COMMAND: DELETE =====
    elif command == "delete":
        if len(args) < 3:
            print("Error: Please provide a task ID.")
            return
        try:
            task_id = int(args[2])
        except ValueError:
            print("Error: Task ID must be a number.")
            return
        delete_tasks(task_id, project)

    # ===== COMMAND: MARK-IN-PROGRESS =====
    elif command == "mark-in-progress":
        if len(args) < 3:
            print("Error: Please provide a task ID.")
            return
        try:
            task_id = int(args[2])
        except ValueError:
            print("Error: Task ID must be a number.")
            return
        mark_in_progress(task_id, project)

    # ===== COMMAND: MARK-DONE =====
    elif command == "mark-done":
        if len(args) < 3:
            print("Error: Please provide a task ID.")
            return
        try:
            task_id = int(args[2])
        except ValueError:
            print("Error: Task ID must be a number.")
            return
        mark_done(task_id, project)

    # ===== COMMAND: LIST =====
    # Enhancement 6: Supports sort:<field> option
    elif command == "list":
        status_filter = None
        sort_by = "id"

        # Parse optional arguments (status filter and sort option)
        for i in range(2, len(args)):
            arg = args[i].lower()
            if arg.startswith("sort:"):
                # Extract sort field from "sort:priority" → "priority"
                sort_by = arg.split(":")[1]
            elif arg in ["todo", "in-progress", "done"]:
                status_filter = arg

        list_tasks(status_filter, sort_by, project)

    # ===== COMMAND: SEARCH (Enhancement 4) =====
    elif command == "search":
        if len(args) < 3:
            print("Error: Please provide a search keyword.")
            print('Usage: python task_cli.py search "keyword"')
            return
        search_tasks(args[2], project)

    # ===== COMMAND: EXPORT (Enhancement 7) =====
    elif command == "export":
        export_to_csv(project)

    # ===== COMMAND: BACKUP (Enhancement 8) =====
    elif command == "backup":
        backup_tasks(project)

    # ===== COMMAND: RESTORE (Enhancement 8) =====
    elif command == "restore":
        if len(args) < 3:
            print("Error: Please provide backup filename.")
            print("Usage: python task_cli.py restore <backup_file>")
            return
        restore_tasks(args[2], project)

    # ===== UNKNOWN COMMAND =====
    else:
        print(f"Error: Unknown command '{command}'")
        print("Run 'python task_cli.py' without arguments to see available commands.")


# Run the main function when script is executed directly
# This prevents main() from running if this file is imported as a module
if __name__ == "__main__":
    main()