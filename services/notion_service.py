import os

class NotionService:
    def __init__(self, token=None):  # token not needed anymore
        self.tasks_file = os.getenv('TASKS_FILE', 'tasks.txt')

    def get_todo_list(self):
        try:
            if not os.path.exists(self.tasks_file):
                return """
                    <li>To add tasks:</li>
                    <li>1. Create a text file named 'tasks.txt'</li>
                    <li>2. Add one task per line with priority like:</li>
                    <li>   HIGH: Complete project presentation</li>
                    <li>   MED: Review weekly reports</li>
                    <li>   LOW: Check emails</li>
                """

            with open(self.tasks_file, 'r') as f:
                tasks = []
                for line in f:
                    line = line.strip()
                    if line:
                        if line.startswith('HIGH:'):
                            tasks.append(f"<li>⭐ {line[5:].strip()}</li>")
                        elif line.startswith('MED:'):
                            tasks.append(f"<li>📝 {line[4:].strip()}</li>")
                        else:
                            tasks.append(f"<li>🔄 {line.replace('LOW:', '').strip()}</li>")

            return "\n".join(tasks) if tasks else "<li>No tasks for today!</li>"

        except Exception as e:
            return f"<li>Unable to read tasks: {str(e)}</li>" 