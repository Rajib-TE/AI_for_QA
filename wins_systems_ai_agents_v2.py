# nodwin_meets_v2.py
# This enhanced version introduces an AI Agent for productivity features.
# It builds directly on v1, adding new functionality while retaining existing features.

import time
import uuid
import re
from typing import Dict, List, Optional, Set

# --- Exceptions from v1 (for Regression Testing) ---
class AuthenticationError(Exception):
    """Custom exception for login failures."""
    pass

class MeetingNotFoundException(Exception):
    """Custom exception for when a meeting ID is invalid."""
    pass

class UserNotAuthorizedError(Exception):
    """Custom exception for actions a user is not permitted to perform."""
    pass

# --- AI-Specific Exception ---
class AIServiceError(Exception):
    """Custom exception for when the AI agent fails."""
    pass

# --- Data Models (Mostly unchanged from v1) ---
class User:
    """Represents a user in the system."""
    def __init__(self, username: str, user_id: str):
        self.username = username
        self.user_id = user_id
        self.is_logged_in = True
        # print(f"INFO: User '{self.username}' created with ID: {self.user_id}") # Less verbose in v2

    def __repr__(self):
        return f"User(username='{self.username}')"

# --- NEW: AI Agent Class ---
class AIAgent:
    """
    A new class to handle AI-powered productivity features like
    transcription, summarization, and action item detection.
    """
    def __init__(self, meeting_id: str):
        self.meeting_id = meeting_id
        self.full_transcript: List[str] = []
        self.action_items: Set[str] = set()
        self.summary: Optional[str] = None
        print(f"AI_AGENT [{meeting_id}]: Initialized and ready.")

    def process_message(self, message: str, author: str):
        """Processes a single message for transcription and action item detection."""
        try:
            # 1. Add to transcript
            transcript_line = f"{author}: {message}"
            self.full_transcript.append(transcript_line)

            # 2. Detect action items (simple keyword-based logic for simulation)
            action_pattern = r'\b(action item|todo|task for|assign to)\b[:\s]*(.*)'
            match = re.search(action_pattern, message, re.IGNORECASE)
            if match:
                action_detail = match.group(2).strip()
                detected_item = f"'{action_detail}' assigned based on message from {author}."
                self.action_items.add(detected_item)
                print(f"AI_AGENT [{self.meeting_id}]: Detected action item: {detected_item}")
        except Exception as e:
            raise AIServiceError(f"Failed to process message: {e}")

    def generate_summary(self) -> str:
        """Generates a summary of the meeting transcript."""
        if not self.full_transcript:
            self.summary = "No content to summarize."
            return self.summary

        # Simulate a complex summarization algorithm
        print(f"AI_AGENT [{self.meeting_id}]: Analyzing {len(self.full_transcript)} lines of transcript...")
        time.sleep(0.5) # Simulate processing time for performance tests

        # A simple summary for demonstration
        first_line = self.full_transcript[0]
        last_line = self.full_transcript[-1]
        self.summary = (
            f"Meeting Summary:\n"
            f"- The meeting started with a message from {first_line.split(':')[0]}.\n"
            f"- A total of {len(self.full_transcript)} messages were exchanged.\n"
            f"- The meeting concluded with a message from {last_line.split(':')[0]}.\n"
            f"- {len(self.action_items)} action items were identified."
        )
        print(f"AI_AGENT [{self.meeting_id}]: Summary generated.")
        return self.summary

# --- Modified Meeting Class to Integrate AI Agent ---
class Meeting:
    """Represents a single meeting session, now with an integrated AI Agent."""
    def __init__(self, meeting_id: str, host: User, enable_ai: bool = True):
        self.meeting_id = meeting_id
        self.host = host
        self.participants: List[User] = [host]
        self.chat_log: List[str] = []
        self.is_active = True
        self.ai_agent: Optional[AIAgent] = AIAgent(meeting_id) if enable_ai else None
        print(f"INFO: Meeting '{self.meeting_id}' created by host '{host.username}'. AI Agent is {'ENABLED' if enable_ai else 'DISABLED'}.")

    def add_participant(self, user: User):
        if user not in self.participants:
            self.participants.append(user)
            print(f"INFO: '{user.username}' has joined meeting '{self.meeting_id}'.")

    def remove_participant(self, user: User):
        if user in self.participants:
            self.participants.remove(user)
            print(f"INFO: '{user.username}' has left meeting '{self.meeting_id}'.")

    def post_chat_message(self, user: User, message: str):
        if user not in self.participants:
            raise UserNotAuthorizedError("User must be in the meeting to chat.")

        if "<script>" in message:
            print("SECURITY_ALERT: Potential XSS attempt detected and blocked.")
            return

        log_entry = f"[{time.ctime()}] {user.username}: {message}"
        self.chat_log.append(log_entry)
        # print(f"CHAT [{self.meeting_id}]: {log_entry}") # Less verbose in v2

        # --- NEW: Integration with AI Agent ---
        if self.ai_agent:
            self.ai_agent.process_message(message, user.username)

    def end_meeting(self, user: User):
        if user.user_id != self.host.user_id:
            raise UserNotAuthorizedError("Only the host can end the meeting.")

        # --- NEW: Trigger final AI processing ---
        if self.ai_agent:
            print(f"AI_AGENT [{self.meeting_id}]: Finalizing analysis as meeting ends...")
            self.ai_agent.generate_summary()

        self.is_active = False
        print(f"INFO: Meeting '{self.meeting_id}' has been ended by the host.")
        return "Meeting ended successfully. AI summary is available."

    # --- NEW: Methods to access AI features ---
    def get_meeting_summary(self, user: User) -> str:
        if user not in self.participants:
            raise UserNotAuthorizedError("Must be a participant to view summary.")
        if not self.ai_agent or self.is_active:
            raise AIServiceError("Summary is only available after the meeting has ended.")
        return self.ai_agent.summary or "Summary has not been generated yet."

    def get_action_items(self, user: User) -> List[str]:
        if user not in self.participants:
            raise UserNotAuthorizedError("Must be a participant to view action items.")
        if not self.ai_agent:
            return ["AI Agent was not enabled for this meeting."]
        return list(self.ai_agent.action_items)


# --- Main Application Server (with minor changes for v2) ---
class NodwinsServer:
    """Simulates the main server, now with ability to create AI-enabled meetings."""
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
        self._user_credentials = {"admin": "password123", "user1": "pass", "qa_tester": "qa_pass"}
        self._initialized = True
        print("INFO: Nodwins Meets v2 Server Initialized.")

    # All other methods from v1 (install, uninstall, login, logout, etc.) are assumed to be here
    # and unchanged unless specified. This is key for regression testing.

    def _check_system_resources(self, ai_enabled: bool = False):
        """Placeholder for performance testing, now considers AI load."""
        load_factor = 1.5 if ai_enabled else 1.0
        print(f"DEBUG: Checking system resources (AI load factor: {load_factor}x)... OK.")
        return True

    def install(self):
        print("SIMULATING: Running installation scripts for v2...")
        time.sleep(1)
        print("SUCCESS: Nodwins Meets v2 installed successfully.")
        return True

    def uninstall(self):
        print("SIMULATING: Removing all application files for v2...")
        time.sleep(1)
        self.__init__()
        print("SUCCESS: Nodwins Meets v2 uninstalled successfully.")
        return True

    def login_user(self, username: str, password: str) -> User:
        if username in self._user_credentials and self._user_credentials[username] == password:
            user_id = f"user-{uuid.uuid4()}"
            user = User(username, user_id)
            self.users[user_id] = user
            return user
        else:
            raise AuthenticationError("Invalid username or password.")

    def logout_user(self, user_id: str):
        if user_id in self.users:
            user = self.users[user_id]
            user.is_logged_in = False
            del self.users[user_id]
            print(f"INFO: User '{user.username}' has been logged out.")
            return True
        return False

    # --- MODIFIED: create_meeting now accepts an AI flag ---
    def create_meeting(self, host: User, enable_ai: bool = True) -> Meeting:
        """Creates a new meeting, with an option to enable/disable the AI Agent."""
        if not self._check_system_resources(ai_enabled=enable_ai):
            raise Exception("System resources are too low to create a new meeting.")

        meeting_id = f"meet-{uuid.uuid4().hex[:8]}"
        meeting = Meeting(meeting_id, host, enable_ai=enable_ai)
        self.meetings[meeting_id] = meeting
        return meeting

    def get_meeting(self, meeting_id: str) -> Optional[Meeting]:
        if meeting_id not in self.meetings or not self.meetings[meeting_id].is_active:
            raise MeetingNotFoundException(f"Meeting with ID '{meeting_id}' not found or has ended.")
        return self.meetings[meeting_id]

    def export_chat_log(self, meeting_id: str, user: User) -> str:
        meeting = self.meetings[meeting_id] # Assume meeting exists for simplicity
        if user not in meeting.participants:
            raise UserNotAuthorizedError("You must be a participant to export the chat log.")

        file_path = f"./{meeting_id}_chat_log_v2.txt"
        report_content = "\n".join(meeting.chat_log)
        with open(file_path, "w") as f:
            f.write(f"--- Chat Log for Meeting {meeting_id} ---\n")
            f.write(report_content)
        print(f"INFO: Chat log exported to {file_path}")
        return file_path