"""
TickTick API Client

This module handles all communication with the TickTick API.
It demonstrates:
- OAuth 2.0 authentication
- API request handling
- Error handling and retries
- Rate limiting

Learning Note: This is a real-world example of integrating with
an external API. Pay attention to error handling and auth flow!
"""

import os
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta

import requests
from requests.auth import HTTPBasicAuth
from rich.console import Console

console = Console()


class TickTickClient:
    """
    TickTick API Client with OAuth authentication.

    The TickTick API uses OAuth 2.0 for authentication. This client
    handles the authentication flow and provides methods to interact
    with tasks, projects, and tags.
    """

    # TickTick API endpoints
    BASE_URL = "https://api.ticktick.com"
    AUTH_URL = f"{BASE_URL}/oauth/token"
    TASKS_URL = f"{BASE_URL}/open/v1/task"
    PROJECT_URL = f"{BASE_URL}/open/v1/project"

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        """
        Initialize the TickTick client.

        Args:
            client_id: OAuth client ID from TickTick Developer settings
            client_secret: OAuth client secret
            username: TickTick account email (for password grant)
            password: TickTick account password (for password grant)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password

        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None

        # Rate limiting
        self.requests_per_minute = 120
        self.request_times: List[datetime] = []

    def authenticate(self) -> bool:
        """
        Authenticate with TickTick API using OAuth 2.0 password grant.

        This gets an access token that we'll use for subsequent API calls.

        Returns:
            True if authentication successful, False otherwise

        Learning Note: OAuth 2.0 has multiple "grant types". We use
        "password grant" here for simplicity, but "authorization code"
        is more secure for production applications.
        """
        console.print("🔐 Authenticating with TickTick...")

        try:
            # Prepare authentication request
            auth = HTTPBasicAuth(self.client_id, self.client_secret)
            data = {
                "grant_type": "password",
                "username": self.username,
                "password": self.password,
                "scope": "tasks:read tasks:write",  # Request necessary permissions
            }

            # Make authentication request
            response = requests.post(
                self.AUTH_URL,
                auth=auth,
                data=data,
                timeout=10
            )

            # Check if successful
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data["access_token"]

                # Calculate when token expires (usually 3600 seconds)
                expires_in = token_data.get("expires_in", 3600)
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)

                console.print("✅ [green]Authentication successful![/green]")
                return True
            else:
                console.print(f"❌ [red]Authentication failed: {response.status_code}[/red]")
                console.print(f"Response: {response.text}")
                return False

        except Exception as e:
            console.print(f"❌ [red]Authentication error: {e}[/red]")
            return False

    def _check_token_validity(self) -> bool:
        """
        Check if current access token is still valid.

        Returns:
            True if token is valid, False if expired or not set
        """
        if not self.access_token:
            return False

        if not self.token_expires_at:
            return False

        # Add 5-minute buffer before expiration
        return datetime.now() < (self.token_expires_at - timedelta(minutes=5))

    def _ensure_authenticated(self):
        """
        Ensure we have a valid access token, re-authenticating if necessary.

        This is called before each API request to handle token expiration.
        """
        if not self._check_token_validity():
            console.print("🔄 Token expired, re-authenticating...")
            if not self.authenticate():
                raise Exception("Failed to authenticate with TickTick")

    def _check_rate_limit(self):
        """
        Check and enforce rate limiting.

        TickTick allows 120 requests per minute. We track request times
        and wait if necessary to avoid hitting the limit.

        Learning Note: Rate limiting is crucial when working with APIs!
        Always respect the API's limits to avoid being blocked.
        """
        now = datetime.now()

        # Remove requests older than 1 minute
        self.request_times = [
            t for t in self.request_times
            if now - t < timedelta(minutes=1)
        ]

        # If at limit, wait until oldest request is 1 minute old
        if len(self.request_times) >= self.requests_per_minute:
            oldest = self.request_times[0]
            wait_time = 60 - (now - oldest).total_seconds()

            if wait_time > 0:
                console.print(f"⏳ Rate limit reached, waiting {wait_time:.1f}s...")
                time.sleep(wait_time)

        # Record this request
        self.request_times.append(now)

    def _make_request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> requests.Response:
        """
        Make an authenticated API request with rate limiting and retries.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Full URL to request
            **kwargs: Additional arguments to pass to requests

        Returns:
            Response object

        Learning Note: This centralizes all API calls, making it easy
        to add logging, retries, error handling, etc. in one place.
        """
        self._ensure_authenticated()
        self._check_rate_limit()

        # Add authentication header
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.access_token}"

        # Make request with retries
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.request(
                    method,
                    url,
                    headers=headers,
                    timeout=10,
                    **kwargs
                )

                # Check for rate limit response
                if response.status_code == 429:
                    wait_time = int(response.headers.get("Retry-After", 60))
                    console.print(f"⏳ Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue

                return response

            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    console.print(f"⚠️  Request failed, retrying... ({attempt + 1}/{max_retries})")
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise e

    def get_tasks(self, project_id: Optional[str] = None) -> List[Dict]:
        """
        Fetch tasks from TickTick.

        Args:
            project_id: Optional project ID to filter tasks

        Returns:
            List of task dictionaries

        Example task structure:
        {
            'id': 'task_id',
            'title': 'Task title',
            'content': 'Task description',
            'priority': 3,  # 0=None, 1=Low, 3=Medium, 5=High
            'dueDate': '2025-11-05T10:00:00.000+0000',
            'status': 0,  # 0=incomplete, 2=complete
            'projectId': 'project_id',
            'tags': ['tag1', 'tag2']
        }
        """
        console.print("📥 Fetching tasks from TickTick...")

        url = self.TASKS_URL
        if project_id:
            url = f"{self.PROJECT_URL}/{project_id}/task"

        response = self._make_request("GET", url)

        if response.status_code == 200:
            tasks = response.json()
            console.print(f"✅ Retrieved {len(tasks)} tasks")
            return tasks
        else:
            console.print(f"❌ Failed to fetch tasks: {response.status_code}")
            return []

    def get_projects(self) -> List[Dict]:
        """
        Fetch all projects from TickTick.

        Returns:
            List of project dictionaries
        """
        console.print("📂 Fetching projects from TickTick...")

        response = self._make_request("GET", self.PROJECT_URL)

        if response.status_code == 200:
            projects = response.json()
            console.print(f"✅ Retrieved {len(projects)} projects")
            return projects
        else:
            console.print(f"❌ Failed to fetch projects: {response.status_code}")
            return []

    def create_task(self, task_data: Dict) -> Optional[Dict]:
        """
        Create a new task in TickTick.

        Args:
            task_data: Dictionary with task properties

        Returns:
            Created task dictionary or None if failed
        """
        console.print(f"➕ Creating task: {task_data.get('title', 'Untitled')}")

        response = self._make_request("POST", self.TASKS_URL, json=task_data)

        if response.status_code == 200:
            task = response.json()
            console.print("✅ Task created successfully")
            return task
        else:
            console.print(f"❌ Failed to create task: {response.status_code}")
            return None

    def update_task(self, task_id: str, task_data: Dict) -> Optional[Dict]:
        """
        Update an existing task.

        Args:
            task_id: ID of task to update
            task_data: Dictionary with updated task properties

        Returns:
            Updated task dictionary or None if failed
        """
        console.print(f"📝 Updating task: {task_id}")

        url = f"{self.TASKS_URL}/{task_id}"
        response = self._make_request("POST", url, json=task_data)

        if response.status_code == 200:
            task = response.json()
            console.print("✅ Task updated successfully")
            return task
        else:
            console.print(f"❌ Failed to update task: {response.status_code}")
            return None


def create_client_from_env() -> TickTickClient:
    """
    Create a TickTick client using environment variables.

    Required environment variables:
    - TICKTICK_CLIENT_ID
    - TICKTICK_CLIENT_SECRET
    - TICKTICK_USERNAME
    - TICKTICK_PASSWORD

    Returns:
        Configured TickTickClient instance
    """
    from dotenv import load_dotenv
    load_dotenv()

    client_id = os.getenv("TICKTICK_CLIENT_ID")
    client_secret = os.getenv("TICKTICK_CLIENT_SECRET")
    username = os.getenv("TICKTICK_USERNAME")
    password = os.getenv("TICKTICK_PASSWORD")

    if not all([client_id, client_secret, username, password]):
        raise ValueError(
            "Missing required environment variables. "
            "Please set TICKTICK_CLIENT_ID, TICKTICK_CLIENT_SECRET, "
            "TICKTICK_USERNAME, and TICKTICK_PASSWORD"
        )

    client = TickTickClient(
        client_id=client_id,
        client_secret=client_secret,
        username=username,
        password=password
    )

    # Authenticate on creation
    if not client.authenticate():
        raise Exception("Failed to authenticate with TickTick")

    return client


# Example usage
if __name__ == "__main__":
    # Test the client
    try:
        client = create_client_from_env()
        tasks = client.get_tasks()

        console.print("\n[bold]Your TickTick Tasks:[/bold]")
        for task in tasks[:5]:  # Show first 5
            title = task.get("title", "Untitled")
            priority = task.get("priority", 0)
            console.print(f"  • {title} (Priority: {priority})")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
