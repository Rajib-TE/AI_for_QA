# nodwin_meets_v1.py
# A synthetic codebase for a basic Python-based conferencing tool.
# This version focuses on core functionalities and is designed to be testable.

import time
import uuid
from typing import Dict, List, Optional

# --- Custom Exceptions for Error Handling Tests ---
class AuthenticationError(Exception):
    """Custom exception for login failures."""
    pass

class MeetingNotFoundException(Exception):
    """Custom exception for when a meeting ID is invalid."""
    pass

class UserNotAuthorizedError(Exception):
    """Custom exception for actions a user is not permitted to perform."""
    pass

# --- Data Models ---
class User:
    """Represents a user in the system."""
    def __init__(self, username: str, user_id: str):
        self.username = username
        self.user_id = user_id
        self.is_logged_in = True
        print(f"INFO: User '{self.username}' created with ID: {self.user_id}")

    def __repr__(self):
        return f"User(username='{self.username}')"

class Meeting:
    """Represents a single meeting session."""
    def __init__(self, meeting_id: str, host: User):
        self.meeting_id = meeting_id
        self.host = host
        self.participants: List[User] = [host]
        self.chat_log: List[str] = []
        self.is_active = True
        print(f"INFO: Meeting '{self.meeting_id}' created by host '{host.username}'.")

    def add_participant(self, user: User):
        """Adds a user to the meeting."""
        if user not in self.participants:
            self.participants.append(user)
            print(f"INFO: '{user.username}' has joined meeting '{self.meeting_id}'.")

    def remove_participant(self, user: User):
        """Removes a user from the meeting."""
        if user in self.participants:
            self.participants.remove(user)
            print(f"INFO: '{user.username}' has left meeting '{self.meeting_id}'.")

    def post_chat_message(self, user: User, message: str):
        """Adds a chat message to the log."""
        if user not in self.participants:
            raise UserNotAuthorizedError("User must be in the meeting to chat.")

        # Input Validation for Security Test Cases
        if "<script>" in message:
            print("SECURITY_ALERT: Potential XSS attempt detected and blocked.")
            return

        log_entry = f"[{time.ctime()}] {user.username}: {message}"
        self.chat_log.append(log_entry)
        print(f"CHAT [{self.meeting_id}]: {log_entry}")

    def end_meeting(self, user: User):
        """Ends the meeting. Only the host can do this."""
        if user.user_id != self.host.user_id:
            raise UserNotAuthorizedError("Only the host can end the meeting.")
        self.is_active = False
        print(f"INFO: Meeting '{self.meeting_id}' has been ended by the host.")
        return "Meeting ended successfully."

# --- Main Application Server (Singleton Simulation) ---
class NodwinsServer:
    """Simulates the main server handling users and meetings."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NodwinsServer, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.users: Dict[str, User] = {}
        self.meetings: Dict[str, Meeting] = {}
        # Dummy database for authentication tests
        self._user_credentials = {"admin": "password123", "user1": "pass"}
        self._initialized = True
        print("INFO: Nodwins Meets v1 Server Initialized.")

    def _check_system_resources(self):
        """Placeholder for performance testing hooks."""
        # In a real app, this would check CPU/memory.
        # For testing, we can simulate high load.
        print("DEBUG: Checking system resources... OK.")
        return True

    def install(self):
        """Simulates installation process for testing."""
        print("SIMULATING: Running installation scripts...")
        time.sleep(1)
        print("SUCCESS: Nodwins Meets v1 installed successfully.")
        return True

    def uninstall(self):
        """Simulates uninstallation process for testing."""
        print("SIMULATING: Removing all application files and registry entries...")
        time.sleep(1)
        # Resetting state for clean testing
        self.__init__()
        print("SUCCESS: Nodwins Meets v1 uninstalled successfully.")
        return True

    def login_user(self, username: str, password: str) -> User:
        """Authenticates a user and returns a User object."""
        if username in self._user_credentials and self._user_credentials[username] == password:
            user_id = f"user-{uuid.uuid4()}"
            user = User(username, user_id)
            self.users[user_id] = user
            return user
        else:
            raise AuthenticationError("Invalid username or password.")

    def logout_user(self, user_id: str):
        """Logs a user out of the system."""
        if user_id in self.users:
            user = self.users[user_id]
            user.is_logged_in = False
            del self.users[user_id]
            print(f"INFO: User '{user.username}' has been logged out.")
            return True
        return False

    def create_meeting(self, host: User) -> Meeting:
        """Creates a new meeting session."""
        if not self._check_system_resources():
            raise Exception("System resources are too low to create a new meeting.")

        meeting_id = f"meet-{uuid.uuid4().hex[:8]}"
        meeting = Meeting(meeting_id, host)
        self.meetings[meeting_id] = meeting
        return meeting

    def get_meeting(self, meeting_id: str) -> Optional[Meeting]:
        """Retrieves an active meeting."""
        if meeting_id not in self.meetings or not self.meetings[meeting_id].is_active:
            raise MeetingNotFoundException(f"Meeting with ID '{meeting_id}' not found or has ended.")
        return self.meetings[meeting_id]

    def export_chat_log(self, meeting_id: str, user: User) -> str:
        """Exports the chat log for a meeting."""
        meeting = self.get_meeting(meeting_id)
        if user not in meeting.participants:
            raise UserNotAuthorizedError("You must be a participant to export the chat log.")

        file_path = f"./{meeting_id}_chat_log.txt"
        report_content = "\n".join(meeting.chat_log)
        with open(file_path, "w") as f:
            f.write(f"--- Chat Log for Meeting {meeting_id} ---\n")
            f.write(report_content)
        print(f"INFO: Chat log exported to {file_path}")
        return file_path