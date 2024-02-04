
import streamlit as st
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
import sqlite3

# Enums for task state and category with automatic values for clarity and simplicity
class TaskState(str, Enum):
    planned = "planned"
    in_progress = "in-progress"
    done = "done"

class TaskCategory(str, Enum):
    school = "school"
    work = "work"
    personal = "personal"

# Task model using Pydantic for data validation
class Task(BaseModel):
    id: int = None
    name: str
    description: str
    state: TaskState = TaskState.planned
    category: TaskCategory
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: str

# Database initialization and operations encapsulated in a context manager for connection handling
def db_connection():
    return sqlite3.connect('tasks.db')

def init_db():
    with db_connection() as conn:
        conn.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            state TEXT,
            category TEXT,
            created_at TEXT,
            created_by TEXT
        )
        ''')

def add_task(task: Task):
    with db_connection() as conn:
        conn.execute("INSERT INTO tasks (name, description, state, category, created_at, created_by) VALUES (?, ?, ?, ?, ?, ?)",
                     (task.name, task.description, task.state.value, task.category.value, task.created_at.isoformat(), task.created_by))

def update_task_state(id, new_state):
    with db_connection() as conn:
        conn.execute("UPDATE tasks SET state = ? WHERE id = ?", (new_state.value, id))

def get_tasks():
    with db_connection() as conn:
        return conn.execute("SELECT id, name, description, state, category, created_at, created_by FROM tasks").fetchall()

init_db()

# Streamlit UI layout for task management
st.title('Task Manager')

with st.form("task_form"):
    # Streamlined input fields for task attributes
    task_name = st.text_input("Name")
    task_description = st.text_area("Description")
    task_state = st.selectbox("State", options=[state.value for state in TaskState])
    task_category = st.selectbox("Category", options=[category.value for category in TaskCategory])
    task_created_by = st.text_input("Created by")
    task_created_at = datetime.combine(st.date_input("Created at", datetime.now()), datetime.min.time())

    # Task submission logic
    if st.form_submit_button("Submit"):
        task = Task(name=task_name, description=task_description, state=TaskState(task_state),
                    category=TaskCategory(task_category), created_at=task_created_at, created_by=task_created_by)
        add_task(task)
        st.success(f"Task '{task.name}' added!")

# Display existing tasks with an option to mark them as done
# Display the task list header
st.write("Tasks:")
cols = st.columns(6)
headers = ["Name", "State", "Category", "Created at", "Created by", "Mark as Done"]
for col, header in zip(cols, headers):
    col.write(header)
st.write("---")

for task in get_tasks():
    cols = st.columns(6)
    for i, detail in enumerate(task[1:6]):
        cols[i].write(detail)
    done = cols[-1].checkbox("Done", key=task[0], value=task[3] == TaskState.done.value)
    if done and task[3] != TaskState.done.value:
        update_task_state(task[0], TaskState.done)
        st.experimental_rerun()
