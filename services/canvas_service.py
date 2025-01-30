from canvasapi import Canvas
import os
from datetime import datetime, timedelta

class CanvasService:
    def __init__(self):
        api_key = os.getenv('CANVAS_API_KEY')
        # Thomas College Canvas URL
        base_url = "https://thomas.instructure.com"
        
        print("\nCanvas Service Debug:")
        print(f"API Key Length: {len(api_key) if api_key else 0}")
        print(f"Base URL: {base_url}")
        
        self.is_configured = False
        if not api_key:
            print("Canvas API key not configured")
            return
            
        try:
            print("Attempting to connect to Canvas...")
            self.canvas = Canvas(base_url, api_key)
            print("Canvas connection established")
            print("Fetching user info...")
            self.user = self.canvas.get_current_user()
            print(f"Successfully connected as user: {self.user.name}")
            self.is_configured = True
        except Exception as e:
            print(f"Canvas setup failed with error: {str(e)}")
            print("Try generating a new token in Canvas Account Settings")

    def get_assignments(self):
        if not self.is_configured:
            return """
                <li>📚 Canvas not configured. To see your assignments:</li>
                <li>1. Go to Canvas Account Settings</li>
                <li>2. Generate a new access token</li>
                <li>3. Add CANVAS_API_KEY to your .env file</li>
            """
            
        try:
            today = datetime.now()
            next_week = today + timedelta(days=7)
            
            # Get all active courses
            courses = self.user.get_courses(enrollment_state='active')
            
            upcoming_assignments = []
            due_today = []
            due_this_week = []
            
            for course in courses:
                assignments = course.get_assignments()
                for assignment in assignments:
                    if not assignment.due_at:
                        continue
                        
                    due_date = datetime.strptime(assignment.due_at, "%Y-%m-%dT%H:%M:%SZ")
                    
                    # Skip past assignments
                    if due_date < today:
                        continue
                        
                    assignment_info = {
                        'name': assignment.name,
                        'course': course.name,
                        'due_date': due_date,
                        'points': assignment.points_possible,
                        'url': assignment.html_url
                    }
                    
                    # Categorize by due date
                    if due_date.date() == today.date():
                        due_today.append(assignment_info)
                    elif due_date <= next_week:
                        due_this_week.append(assignment_info)
            
            # Sort by due date
            due_today.sort(key=lambda x: x['due_date'])
            due_this_week.sort(key=lambda x: x['due_date'])
            
            # Format the output
            output = []
            
            if due_today:
                output.append("<li><strong>🚨 Due Today:</strong></li>")
                for assignment in due_today:
                    time_str = assignment['due_date'].strftime("%I:%M %p")
                    output.append(
                        f"<li>📝 {assignment['name']} ({assignment['course']}) - "
                        f"Due at {time_str} - "
                        f"<a href='{assignment['url']}'>View</a></li>"
                    )
            
            if due_this_week:
                output.append("<li><strong>📅 Due This Week:</strong></li>")
                for assignment in due_this_week:
                    date_str = assignment['due_date'].strftime("%A, %B %d")
                    output.append(
                        f"<li>📚 {assignment['name']} ({assignment['course']}) - "
                        f"Due {date_str} - "
                        f"<a href='{assignment['url']}'>View</a></li>"
                    )
            
            if not output:
                return "<li>🎉 No upcoming assignments this week!</li>"
                
            return "\n".join(output)

        except Exception as e:
            return f"<li>Unable to fetch Canvas assignments: {str(e)}</li>" 