from datetime import datetime
from googleapiclient.discovery import build
from ..auth_manager import auth_manager

class GoogleTasksService:    
    def __init__(self):
        self.service = None
        self.default_tasklist_id = None
        self._initialize_service()
    
    def _initialize_service(self):
        try:
            creds = auth_manager.get_credentials()
            self.service = build('tasks', 'v1', credentials=creds)
            self._get_default_tasklist()
        except Exception as e:
            print(f"Failed to initialize Tasks service: {e}")
    
    def _get_default_tasklist(self):
        if not self.service:
            return
        
        try:
            results = self.service.tasklists().list().execute()
            tasklists = results.get('items', [])
            
            if tasklists:
                self.default_tasklist_id = tasklists[0]['id']
            else:
                raise Exception("No task lists found")
                
        except Exception as e:
            print(f"Error getting task lists: {e}")
    
    def create_task(self, data_item):
        if not self.service or not self.default_tasklist_id:
            scope_check = auth_manager.check_scopes()
            if not scope_check.get('has_tasks', False):
                return {
                    'success': False,
                    'error': 'Missing Google Tasks permissions. Please re-authenticate.',
                    'task_data': data_item,
                    'fix': 'Run: auth_manager.force_reauth()'
                }
            else:
                return {
                    'success': False,
                    'error': 'Tasks service not properly initialized',
                    'task_data': data_item
                }
        
        try:
            task_body = {
                'title': data_item.get('title', 'No Title'),
            }
            
            # Add description as notes
            description = data_item.get('description')
            if description:
                task_body['notes'] = description
            
            # Add due date
            due_date = data_item.get('due_date')
            if due_date:
                try:
                    if isinstance(due_date, str):
                        parsed_date = datetime.strptime(due_date, '%Y-%m-%d')
                        task_body['due'] = parsed_date.strftime('%Y-%m-%dT00:00:00.000Z')
                except ValueError as e:
                    print(f"Invalid due date format: {due_date}. Expected YYYY-MM-DD")
            
            # Create the task
            result = self.service.tasks().insert(
                tasklist=self.default_tasklist_id,
                body=task_body
            ).execute()
            
            return {
                'success': True,
                'task_id': result.get('id'),
                'title': result.get('title'),
                'due': result.get('due'),
                'status': result.get('status'),
                'webViewLink': result.get('webViewLink')
            }
            
        except Exception as e:
            error_msg = str(e)
            if "insufficient authentication scopes" in error_msg.lower():
                return {
                    'success': False,
                    'error': 'Insufficient authentication scopes for Google Tasks',
                    'task_data': data_item,
                    'fix': 'Delete token.json and restart the application to re-authenticate'
                }
            else:
                return {
                    'success': False,
                    'error': f'Failed to create task: {error_msg}',
                    'task_data': data_item
                }

# Initialize the service
tasks_service = GoogleTasksService()

def create_google_task(data_item):
    return tasks_service.create_task(data_item)