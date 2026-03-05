# 📋 Task Tracker CLI

Project URL: [Task Tracker - roadmap.sh]([https://roadmap.sh/projects/task-tracker](https://roadmap.sh/projects/task-tracker))

A command-line task tracker built with Python. No external libraries used.

## Features

- ✅ Add, Update, Delete tasks
- ✅ Mark tasks as in-progress or done
- ✅ List and filter tasks by status
- 🎨 Colored output (ANSI codes)
- ⚡ Priority levels (high/medium/low)
- 🔍 Search tasks by keyword
- 📶 Sort tasks (by id/status/priority/date)
- 📄 Export tasks to CSV
- 💾 Backup & Restore
- 📁 Multiple project support

## Requirements

- Python 3.6 or higher

## Usage

```bash
python task_cli.py <command> [arguments] [--project <name>]
```

### Commands

```bash
# Add tasks (with optional priority: high/medium/low)
python task_cli.py add "Buy groceries"
python task_cli.py add "Fix critical bug" high

# Update a task
python task_cli.py update 1 "Buy organic groceries"

# Delete a task
python task_cli.py delete 1

# Mark task status
python task_cli.py mark-in-progress 1
python task_cli.py mark-done 1

# List tasks
python task_cli.py list                    # All tasks
python task_cli.py list todo               # Filter by status
python task_cli.py list in-progress
python task_cli.py list done
python task_cli.py list sort:priority      # Sort tasks
python task_cli.py list todo sort:date     # Filter + Sort

# Search tasks
python task_cli.py search "groceries"

# Export to CSV
python task_cli.py export

# Backup & Restore
python task_cli.py backup
python task_cli.py restore tasks_backup_20260305_143000.json

# Multiple projects
python task_cli.py add "Design homepage" --project work
python task_cli.py list --project work
```

## Task Properties

| Property | Description |
|----------|-------------|
| id | Unique task identifier |
| description | Task description text |
| status | todo, in-progress, or done |
| priority | high, medium, or low |
| createdAt | Timestamp when task was created |
| updatedAt | Timestamp when task was last modified |

## Data Storage

Tasks are stored in a JSON file (`task.json`) in the current directory. The file is created automatically when you add your first task.
