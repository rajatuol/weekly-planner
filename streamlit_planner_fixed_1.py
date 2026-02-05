import streamlit as st
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict

# Page config
st.set_page_config(page_title="Weekly Planner", layout="wide", initial_sidebar_state="expanded")

# CSS styling
st.markdown("""
<style>
    .task-complete { opacity: 0.6; text-decoration: line-through; }
    .task-high { border-left: 4px solid #ff4444; }
    .task-medium { border-left: 4px solid #ffaa00; }
    .task-low { border-left: 4px solid #44aa44; }
    .day-header { font-size: 1.3em; font-weight: bold; margin-top: 20px; }
    .habit-box { background-color: #f0f8ff; padding: 10px; border-radius: 5px; margin: 5px 0; }
    .goal-box { background-color: #fff0f8; padding: 10px; border-radius: 5px; margin: 5px 0; }
    .note-box { background-color: #fffacd; padding: 10px; border-radius: 5px; margin: 5px 0; }
    .backlog-box { background-color: #fff5ee; padding: 10px; border-radius: 5px; margin: 5px 0; }
</style>
""", unsafe_allow_html=True)

class Task:
    def __init__(self, title, category, priority=1, due_date=None, completed=False, task_id=None):
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
            priority=data.get("priority", 1),
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
        """Get Monday of the week for a given date"""
        # Convert to date if it's a datetime object
        if isinstance(date, datetime):
            date = date.date()
        # Subtract days to get to Monday
        return date - timedelta(days=date.weekday())
    
    @staticmethod
    def get_days_of_week():
        """Return list of days for current week"""
        today = datetime.now().date()
        week_start = WeeklyPlanner.get_week_start(today)
        days = []
        for i in range(7):
            days.append(week_start + timedelta(days=i))
        return days
    
    def load_data(self):
        """Load tasks from JSON file"""
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                data = json.load(f)
                self.tasks = [Task.from_dict(t) for t in data.get("tasks", [])]
                self.backlog = [Task.from_dict(t) for t in data.get("backlog", [])]
    
    def save_data(self):
        """Save tasks to JSON file"""
        data = {
            "tasks": [t.to_dict() for t in self.tasks],
            "backlog": [t.to_dict() for t in self.backlog]
        }
        with open(self.filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_task(self, title, category, priority=1, due_date=None):
        """Add a new task"""
        task = Task(title, category, priority, due_date)
        self.tasks.append(task)
        self.save_data()
        return task.id
    
    def mark_complete(self, task_id):
        """Mark a task as complete"""
        for task in self.tasks + self.backlog:
            if task.id == task_id:
                task.completed = not task.completed
                self.save_data()
                return
    
    def delete_task(self, task_id):
        """Delete a task"""
        self.tasks = [t for t in self.tasks if t.id != task_id]
        self.backlog = [t for t in self.backlog if t.id != task_id]
        self.save_data()
    
    def move_incomplete_tasks(self):
        """Move incomplete tasks to next day or backlog"""
        today = datetime.now().date()
        days = self.get_days_of_week()
        week_end = days[-1]
        
        for task in self.tasks[:]:
            if not task.completed and task.due_date:
                task_date = datetime.fromisoformat(task.due_date).date()
                
                if task_date == today and task.category == "daily":
                    task.due_date = (today + timedelta(days=1)).isoformat()
                
                if task_date < today and task_date >= days[0]:
                    self.tasks.remove(task)
                    task.due_date = None
                    self.backlog.append(task)
        
        self.save_data()
    
    def get_tasks_for_date(self, date):
        """Get tasks for a specific date"""
        return [t for t in self.tasks if t.due_date and datetime.fromisoformat(t.due_date).date() == date and t.category == "daily"]
    
    def get_habits(self):
        """Get all habits"""
        return [t for t in self.tasks if t.category == "habit"]
    
    def get_weekly_goals(self):
        """Get all weekly goals"""
        return [t for t in self.tasks if t.category == "weekly_goal"]
    
    def get_notes(self):
        """Get all notes"""
        return [t for t in self.tasks if t.category == "note"]
    
    def move_to_date(self, task_id, new_date_str):
        """Move task to a different date"""
        for task in self.tasks:
            if task.id == task_id:
                task.due_date = new_date_str
                self.save_data()
                return
    
    def move_to_backlog(self, task_id):
        """Move task to backlog"""
        for task in self.tasks[:]:
            if task.id == task_id:
                self.tasks.remove(task)
                task.due_date = None
                self.backlog.append(task)
                self.save_data()
                return

# Initialize session state
if "planner" not in st.session_state:
    st.session_state.planner = WeeklyPlanner()
    st.session_state.planner.move_incomplete_tasks()

planner = st.session_state.planner

# Header
st.title("📅 Weekly Planner")
week_start = WeeklyPlanner.get_week_start(datetime.now())
st.subheader(f"Week of {week_start}")

# Sidebar for adding tasks
with st.sidebar:
    st.header("➕ Add Task")
    
    task_type = st.radio("Task Type", ["Daily Task", "Habit", "Weekly Goal", "Note"])
    task_title = st.text_input("Task Title")
    
    if task_type == "Daily Task":
        task_date = st.date_input("Date", value=datetime.now().date())
        task_priority = st.select_slider("Priority", options=[1, 2, 3], value=1, format_func=lambda x: ["High 🔥", "Medium ⭐", "Low ✓"][x-1])
        if st.button("Add Task"):
            planner.add_task(task_title, "daily", task_priority, task_date.isoformat())
            st.success("✓ Task added!")
            st.rerun()
    
    elif task_type == "Habit":
        task_priority = st.select_slider("Priority", options=[1, 2, 3], value=1, format_func=lambda x: ["High 🔥", "Medium ⭐", "Low ✓"][x-1])
        if st.button("Add Habit"):
            planner.add_task(task_title, "habit", task_priority)
            st.success("✓ Habit added!")
            st.rerun()
    
    elif task_type == "Weekly Goal":
        task_priority = st.select_slider("Priority", options=[1, 2, 3], value=1, format_func=lambda x: ["High 🔥", "Medium ⭐", "Low ✓"][x-1])
        if st.button("Add Goal"):
            planner.add_task(task_title, "weekly_goal", task_priority)
            st.success("✓ Goal added!")
            st.rerun()
    
    else:  # Note
        if st.button("Add Note"):
            planner.add_task(task_title, "note")
            st.success("✓ Note added!")
            st.rerun()

# Main content tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📆 Week", "✨ Habits", "🎯 Goals", "📝 Notes", "⏳ Backlog"])

with tab1:
    st.header("Daily Tasks")
    days_of_week = WeeklyPlanner.get_days_of_week()
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    for idx, date in enumerate(days_of_week):
        day_name = day_names[idx]
        is_today = date == datetime.now().date()
        header_emoji = "📌" if is_today else "📅"
        
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            st.subheader(f"{header_emoji} {day_name} - {date}")
        
        tasks = planner.get_tasks_for_date(date)
        
        if tasks:
            for task in sorted(tasks, key=lambda x: -x.priority):
                col1, col2, col3, col4 = st.columns([0.6, 0.15, 0.15, 0.1])
                
                with col1:
                    status = "✅" if task.completed else "○"
                    priority_emoji = "🔥" if task.priority == 1 else "⭐" if task.priority == 2 else "✓"
                    if st.checkbox(f"{status} {priority_emoji} {task.title}", value=task.completed, key=task.id):
                        planner.mark_complete(task.id)
                        st.rerun()
                
                with col2:
                    if st.button("Move", key=f"move_{task.id}"):
                        st.session_state.move_modal = task.id
                
                with col3:
                    if st.button("Backlog", key=f"backlog_{task.id}"):
                        planner.move_to_backlog(task.id)
                        st.rerun()
                
                with col4:
                    if st.button("🗑", key=f"delete_{task.id}"):
                        planner.delete_task(task.id)
                        st.rerun()
        else:
            st.info("No tasks for this day")
        
        st.divider()

with tab2:
    st.header("Habits")
    habits = planner.get_habits()
    
    if habits:
        for habit in habits:
            col1, col2, col3 = st.columns([0.7, 0.15, 0.15])
            
            with col1:
                priority_emoji = "🔥" if habit.priority == 1 else "⭐" if habit.priority == 2 else "✓"
                if st.checkbox(f"{priority_emoji} {habit.title}", value=habit.completed, key=habit.id):
                    planner.mark_complete(habit.id)
                    st.rerun()
            
            with col2:
                if st.button("Delete", key=f"delete_habit_{habit.id}"):
                    planner.delete_task(habit.id)
                    st.rerun()
    else:
        st.info("No habits yet. Add one in the sidebar!")

with tab3:
    st.header("Weekly Goals")
    goals = planner.get_weekly_goals()
    
    if goals:
        completed = sum(1 for g in goals if g.completed)
        st.progress(completed / len(goals) if goals else 0, text=f"{completed}/{len(goals)} completed")
        
        for goal in goals:
            col1, col2, col3 = st.columns([0.7, 0.15, 0.15])
            
            with col1:
                priority_emoji = "🔥" if goal.priority == 1 else "⭐" if goal.priority == 2 else "✓"
                if st.checkbox(f"{priority_emoji} {goal.title}", value=goal.completed, key=goal.id):
                    planner.mark_complete(goal.id)
                    st.rerun()
            
            with col2:
                if st.button("Delete", key=f"delete_goal_{goal.id}"):
                    planner.delete_task(goal.id)
                    st.rerun()
    else:
        st.info("No weekly goals yet. Add one in the sidebar!")

with tab4:
    st.header("Notes")
    notes = planner.get_notes()
    
    if notes:
        for note in notes:
            col1, col2 = st.columns([0.85, 0.15])
            
            with col1:
                st.markdown(f"📝 {note.title}")
            
            with col2:
                if st.button("Delete", key=f"delete_note_{note.id}"):
                    planner.delete_task(note.id)
                    st.rerun()
    else:
        st.info("No notes yet. Add one in the sidebar!")

with tab5:
    st.header("Backlog")
    
    if planner.backlog:
        st.write(f"**Total: {len(planner.backlog)} items**")
        
        for task in sorted(planner.backlog, key=lambda x: -x.priority):
            col1, col2, col3, col4 = st.columns([0.5, 0.2, 0.15, 0.15])
            
            with col1:
                priority_emoji = "🔥" if task.priority == 1 else "⭐" if task.priority == 2 else "✓"
                if st.checkbox(f"{priority_emoji} {task.title}", value=task.completed, key=f"backlog_{task.id}"):
                    planner.mark_complete(task.id)
                    st.rerun()
            
            with col2:
                new_date = st.date_input("Move to date", key=f"move_date_{task.id}")
                if st.button("Move", key=f"confirm_move_{task.id}"):
                    planner.move_to_date(task.id, new_date.isoformat())
                    st.rerun()
            
            with col3:
                if st.button("Delete", key=f"delete_backlog_{task.id}"):
                    planner.delete_task(task.id)
                    st.rerun()
    else:
        st.success("✓ Backlog is empty!")

# Footer
st.divider()
col1, col2 = st.columns(2)
with col1:
    if st.button("🔄 Refresh & Move Tasks"):
        planner.move_incomplete_tasks()
        st.rerun()
