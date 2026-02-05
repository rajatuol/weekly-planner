import streamlit as st
import json
import os
from datetime import datetime, timedelta

# Page config
st.set_page_config(page_title="Weekly Planner", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for notebook aesthetic
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Caveat:wght@400;700&family=Indie+Flower&display=swap');
    
    * {
        font-family: 'Indie Flower', cursive;
    }
    
    .main {
        background-color: #faf8f3;
    }
    
    .stApp {
        background-color: #faf8f3;
    }
    
    .title-text {
        font-family: 'Caveat', cursive;
        font-size: 48px;
        font-weight: 700;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 30px;
    }
    
    .week-header {
        font-family: 'Caveat', cursive;
        font-size: 32px;
        color: #34495e;
        border-bottom: 3px solid #8b7355;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    
    .day-container {
        background-color: #fffdf9;
        border: 2px solid #d4af8e;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 20px;
        min-height: 200px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .day-title {
        font-family: 'Caveat', cursive;
        font-size: 24px;
        color: #2c3e50;
        font-weight: 700;
        margin-bottom: 12px;
        border-bottom: 2px dotted #c9a876;
        padding-bottom: 8px;
    }
    
    .task-item {
        background-color: #fffef8;
        padding: 8px 12px;
        margin-bottom: 8px;
        border-left: 4px solid #8b7355;
        border-radius: 3px;
        font-size: 15px;
        color: #2c3e50;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .task-item.completed {
        opacity: 0.5;
        text-decoration: line-through;
    }
    
    .section-title {
        font-family: 'Caveat', cursive;
        font-size: 28px;
        color: #2c3e50;
        border-bottom: 2px solid #8b7355;
        padding-bottom: 8px;
        margin-top: 30px;
        margin-bottom: 15px;
    }
    
    .backlog-item {
        background-color: #fff9f0;
        padding: 10px;
        margin-bottom: 8px;
        border-left: 4px solid #d89a5c;
        border-radius: 3px;
        font-size: 14px;
        color: #2c3e50;
    }
    
    .habit-item {
        background-color: #f0f8ff;
        padding: 8px 12px;
        margin-bottom: 8px;
        border-left: 4px solid #5b9bd5;
        border-radius: 3px;
        font-size: 14px;
        color: #2c3e50;
    }
    
    .goal-item {
        background-color: #fff5f0;
        padding: 8px 12px;
        margin-bottom: 8px;
        border-left: 4px solid #e74c3c;
        border-radius: 3px;
        font-size: 14px;
        color: #2c3e50;
    }
    
    .note-item {
        background-color: #fffacd;
        padding: 8px 12px;
        margin-bottom: 8px;
        border-left: 4px solid #f39c12;
        border-radius: 3px;
        font-size: 14px;
        color: #2c3e50;
    }
    
    .sidebar-add {
        background-color: #fffdf9;
        border: 2px solid #8b7355;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    .sidebar-title {
        font-family: 'Caveat', cursive;
        font-size: 24px;
        color: #2c3e50;
        margin-bottom: 15px;
        font-weight: 700;
    }
    
    .stButton button {
        font-family: 'Indie Flower', cursive;
        font-size: 16px;
        background-color: #8b7355 !important;
        color: white !important;
        border-radius: 5px !important;
        width: 100%;
    }
    
    .stCheckbox {
        font-family: 'Indie Flower', cursive;
    }
    
    .stTextInput input {
        font-family: 'Indie Flower', cursive !important;
    }
    
    .stSelectSlider {
        font-family: 'Indie Flower', cursive;
    }
    
    .date-text {
        font-family: 'Indie Flower', cursive;
        color: #7f8c8d;
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)

class Task:
    def __init__(self, title, category, priority=2, due_date=None, completed=False, task_id=None):
        self.id = task_id or datetime.now().isoformat()
        self.title = title
        self.category = category
        self.priority = priority
        self.due_date = due_date
        self.completed = completed
        self.created_date = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "priority": self.priority,
            "due_date": self.due_date,
            "completed": self.completed,
            "created_date": self.created_date
        }
    
    @staticmethod
    def from_dict(data):
        return Task(
            title=data["title"],
            category=data["category"],
            priority=data.get("priority", 2),
            due_date=data.get("due_date"),
            completed=data.get("completed", False),
            task_id=data.get("id")
        )

class WeeklyPlanner:
    def __init__(self, filename="planner_data.json"):
        self.filename = filename
        self.tasks = []
        self.backlog = []
        self.load_data()
    
    @staticmethod
    def get_week_start(date):
        if isinstance(date, datetime):
            date = date.date()
        return date - timedelta(days=date.weekday())
    
    @staticmethod
    def get_days_of_week():
        today = datetime.now().date()
        week_start = WeeklyPlanner.get_week_start(today)
        days = []
        for i in range(7):
            days.append(week_start + timedelta(days=i))
        return days
    
    @staticmethod
    def format_date(date_obj):
        """Format date as DD/MM/YYYY"""
        if isinstance(date_obj, str):
            date_obj = datetime.fromisoformat(date_obj).date()
        return date_obj.strftime("%d/%m/%Y")
    
    def load_data(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                data = json.load(f)
                self.tasks = [Task.from_dict(t) for t in data.get("tasks", [])]
                self.backlog = [Task.from_dict(t) for t in data.get("backlog", [])]
    
    def save_data(self):
        data = {
            "tasks": [t.to_dict() for t in self.tasks],
            "backlog": [t.to_dict() for t in self.backlog]
        }
        with open(self.filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_task(self, title, category, priority=2, due_date=None):
        task = Task(title, category, priority, due_date)
        self.tasks.append(task)
        self.save_data()
        return task.id
    
    def mark_complete(self, task_id):
        for task in self.tasks + self.backlog:
            if task.id == task_id:
                task.completed = not task.completed
                self.save_data()
                return
    
    def delete_task(self, task_id):
        self.tasks = [t for t in self.tasks if t.id != task_id]
        self.backlog = [t for t in self.backlog if t.id != task_id]
        self.save_data()
    
    def move_incomplete_tasks(self):
        """Move incomplete tasks to next day or backlog"""
        today = datetime.now().date()
        days = self.get_days_of_week()
        
        for task in self.tasks[:]:
            if not task.completed and task.due_date:
                task_date = datetime.fromisoformat(task.due_date).date()
                
                # Move to next day if not done today
                if task_date == today and task.category == "daily":
                    task.due_date = (today + timedelta(days=1)).isoformat()
                
                # Move to backlog if past week end
                if task_date < today and task_date >= days[0]:
                    self.tasks.remove(task)
                    task.due_date = None
                    self.backlog.append(task)
        
        self.save_data()
    
    def get_tasks_for_date(self, date):
        return [t for t in self.tasks if t.due_date and datetime.fromisoformat(t.due_date).date() == date and t.category == "daily"]
    
    def get_habits(self):
        return [t for t in self.tasks if t.category == "habit"]
    
    def get_goals(self):
        return [t for t in self.tasks if t.category == "goal"]
    
    def get_notes(self):
        return [t for t in self.tasks if t.category == "note"]
    
    def move_to_backlog(self, task_id):
        for task in self.tasks[:]:
            if task.id == task_id:
                self.tasks.remove(task)
                task.due_date = None
                self.backlog.append(task)
                self.save_data()
                return
    
    def move_to_date(self, task_id, new_date):
        for task in self.tasks + self.backlog:
            if task.id == task_id:
                task.due_date = new_date
                if task in self.backlog:
                    self.backlog.remove(task)
                    self.tasks.append(task)
                self.save_data()
                return

# Initialize session state
if "planner" not in st.session_state:
    st.session_state.planner = WeeklyPlanner()
    st.session_state.planner.move_incomplete_tasks()

planner = st.session_state.planner

# Main title
st.markdown('<div class="title-text">Weekly Planner</div>', unsafe_allow_html=True)

# Create columns: main content (wider) and sidebar (right)
col_main, col_sidebar = st.columns([3, 1])

# MAIN CONTENT
with col_main:
    # Week header
    week_start = planner.get_week_start(datetime.now())
    st.markdown(f'<div class="week-header">Week of {planner.format_date(week_start)}</div>', unsafe_allow_html=True)
    
    # Display 7 days in grid
    days_of_week = planner.get_days_of_week()
    day_names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    
    # First row: Sun, Mon, Tue, Wed, Thu
    cols = st.columns(5)
    for idx in range(5):
        with cols[idx]:
            date = days_of_week[idx]
            day_name = day_names[idx]
            is_today = date == datetime.now().date()
            
            with st.container():
                st.markdown(f'<div class="day-container">', unsafe_allow_html=True)
                st.markdown(f'<div class="day-title">{day_name}</div>', unsafe_allow_html=True)
                
                tasks = planner.get_tasks_for_date(date)
                
                if tasks:
                    for task in sorted(tasks, key=lambda x: -x.priority):
                        col_check, col_task = st.columns([0.15, 0.85])
                        with col_check:
                            if st.checkbox("", value=task.completed, key=f"task_{task.id}"):
                                planner.mark_complete(task.id)
                                st.rerun()
                        
                        with col_task:
                            task_class = "completed" if task.completed else ""
                            st.markdown(f'<div class="task-item {task_class}">{task.title}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="task-item" style="opacity: 0.3;">No tasks</div>', unsafe_allow_html=True)
                
                st.markdown(f'<p class="date-text">{planner.format_date(date)}</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
    
    # Second row: Fri, Sat
    cols = st.columns(5)
    
    # Friday
    with cols[0]:
        date = days_of_week[5]
        day_name = day_names[5]
        
        st.markdown(f'<div class="day-container">', unsafe_allow_html=True)
        st.markdown(f'<div class="day-title">{day_name}</div>', unsafe_allow_html=True)
        
        tasks = planner.get_tasks_for_date(date)
        
        if tasks:
            for task in sorted(tasks, key=lambda x: -x.priority):
                col_check, col_task = st.columns([0.15, 0.85])
                with col_check:
                    if st.checkbox("", value=task.completed, key=f"task_{task.id}"):
                        planner.mark_complete(task.id)
                        st.rerun()
                
                with col_task:
                    task_class = "completed" if task.completed else ""
                    st.markdown(f'<div class="task-item {task_class}">{task.title}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="task-item" style="opacity: 0.3;">No tasks</div>', unsafe_allow_html=True)
        
        st.markdown(f'<p class="date-text">{planner.format_date(date)}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Saturday
    with cols[1]:
        date = days_of_week[6]
        day_name = day_names[6]
        
        st.markdown(f'<div class="day-container">', unsafe_allow_html=True)
        st.markdown(f'<div class="day-title">{day_name}</div>', unsafe_allow_html=True)
        
        tasks = planner.get_tasks_for_date(date)
        
        if tasks:
            for task in sorted(tasks, key=lambda x: -x.priority):
                col_check, col_task = st.columns([0.15, 0.85])
                with col_check:
                    if st.checkbox("", value=task.completed, key=f"task_{task.id}"):
                        planner.mark_complete(task.id)
                        st.rerun()
                
                with col_task:
                    task_class = "completed" if task.completed else ""
                    st.markdown(f'<div class="task-item {task_class}">{task.title}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="task-item" style="opacity: 0.3;">No tasks</div>', unsafe_allow_html=True)
        
        st.markdown(f'<p class="date-text">{planner.format_date(date)}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Backlog, Notes, Habits sections below
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="section-title">Back Log</div>', unsafe_allow_html=True)
        if planner.backlog:
            for task in sorted(planner.backlog, key=lambda x: -x.priority):
                col_check, col_task = st.columns([0.15, 0.85])
                with col_check:
                    if st.checkbox("", value=task.completed, key=f"backlog_{task.id}"):
                        planner.mark_complete(task.id)
                        st.rerun()
                
                with col_task:
                    task_class = "completed" if task.completed else ""
                    st.markdown(f'<div class="backlog-item" style="opacity: 0.7;">{task.title}</div>', unsafe_allow_html=True)
                
                col_move, col_delete = st.columns(2)
                with col_move:
                    new_date = st.date_input("Move to", key=f"move_{task.id}", label_visibility="collapsed")
                    if st.button("Move", key=f"btn_move_{task.id}", use_container_width=True):
                        planner.move_to_date(task.id, new_date.isoformat())
                        st.rerun()
                
                with col_delete:
                    if st.button("Delete", key=f"btn_del_bl_{task.id}", use_container_width=True):
                        planner.delete_task(task.id)
                        st.rerun()
        else:
            st.markdown('<div class="backlog-item">All caught up!</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="section-title">Notes</div>', unsafe_allow_html=True)
        notes = planner.get_notes()
        if notes:
            for note in notes:
                col_note, col_del = st.columns([0.85, 0.15])
                with col_note:
                    st.markdown(f'<div class="note-item">{note.title}</div>', unsafe_allow_html=True)
                with col_del:
                    if st.button("X", key=f"del_note_{note.id}"):
                        planner.delete_task(note.id)
                        st.rerun()
        else:
            st.markdown('<div class="note-item">No notes</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="section-title">Habits</div>', unsafe_allow_html=True)
        habits = planner.get_habits()
        if habits:
            for habit in habits:
                if st.checkbox(habit.title, value=habit.completed, key=f"habit_{habit.id}"):
                    planner.mark_complete(habit.id)
                    st.rerun()
        else:
            st.markdown('<div class="habit-item">No habits</div>', unsafe_allow_html=True)

# SIDEBAR (RIGHT)
with col_sidebar:
    st.markdown('<div class="sidebar-add">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">Add Task</div>', unsafe_allow_html=True)
    
    task_type = st.radio("Type", ["Task", "Habit", "Goal", "Note"], label_visibility="collapsed")
    task_title = st.text_input("Title", placeholder="Task name", label_visibility="collapsed")
    
    if task_type == "Task":
        task_date = st.date_input("Date", value=datetime.now().date(), label_visibility="collapsed")
        if st.button("Add Task", use_container_width=True):
            if task_title:
                planner.add_task(task_title, "daily", 2, task_date.isoformat())
                st.rerun()
    
    elif task_type == "Habit":
        if st.button("Add Habit", use_container_width=True):
            if task_title:
                planner.add_task(task_title, "habit")
                st.rerun()
    
    elif task_type == "Goal":
        if st.button("Add Goal", use_container_width=True):
            if task_title:
                planner.add_task(task_title, "goal")
                st.rerun()
    
    else:  # Note
        if st.button("Add Note", use_container_width=True):
            if task_title:
                planner.add_task(task_title, "note")
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("Refresh", use_container_width=True):
        planner.move_incomplete_tasks()
        st.rerun()
