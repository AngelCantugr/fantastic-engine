"""
Snapshot engine for capturing workspace state
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
import os
import json
import subprocess
from pathlib import Path

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import git
import psutil

Base = declarative_base()


class Snapshot(Base):
    __tablename__ = "snapshots"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    project_path = Column(String(500), nullable=False)
    git_branch = Column(String(100), nullable=True)
    git_commit = Column(String(40), nullable=True)
    editor_state = Column(JSON, nullable=True)
    terminal_state = Column(JSON, nullable=True)
    browser_tabs = Column(JSON, nullable=True)
    environment_vars = Column(JSON, nullable=True)
    running_processes = Column(JSON, nullable=True)
    ai_summary = Column(Text, nullable=True)


class SnapshotEngine:
    def __init__(self, db_url: str = "sqlite:///./context_snapshots.db"):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        SessionLocal = sessionmaker(bind=self.engine)
        self.session = SessionLocal()

    def create_snapshot(
        self,
        project_path: str,
        name: Optional[str] = None,
        include_ai_summary: bool = True,
    ) -> Snapshot:
        """Create a snapshot of current workspace"""
        project_path = os.path.abspath(project_path)

        # Git state
        git_state = self._capture_git_state(project_path)

        # Editor state (VS Code detection)
        editor_state = self._capture_editor_state(project_path)

        # Terminal state
        terminal_state = self._capture_terminal_state()

        # Environment variables (filtered)
        env_vars = self._capture_env_vars()

        # Running processes
        processes = self._capture_processes()

        # Create snapshot
        snapshot = Snapshot(
            name=name or f"Auto-snapshot {datetime.now().strftime('%H:%M')}",
            timestamp=datetime.utcnow(),
            project_path=project_path,
            git_branch=git_state.get("branch"),
            git_commit=git_state.get("commit"),
            editor_state=editor_state,
            terminal_state=terminal_state,
            environment_vars=env_vars,
            running_processes=processes,
        )

        if include_ai_summary:
            snapshot.ai_summary = self._generate_ai_summary(snapshot)

        self.session.add(snapshot)
        self.session.commit()

        return snapshot

    def list_snapshots(
        self,
        project_path: Optional[str] = None,
        limit: int = 10,
    ) -> List[Snapshot]:
        """List recent snapshots"""
        query = self.session.query(Snapshot).order_by(Snapshot.timestamp.desc())

        if project_path:
            query = query.filter_by(project_path=os.path.abspath(project_path))

        return query.limit(limit).all()

    def get_snapshot(self, snapshot_id: int) -> Optional[Snapshot]:
        """Get specific snapshot"""
        return self.session.query(Snapshot).filter_by(id=snapshot_id).first()

    def delete_snapshot(self, snapshot_id: int) -> None:
        """Delete a snapshot"""
        snapshot = self.get_snapshot(snapshot_id)
        if snapshot:
            self.session.delete(snapshot)
            self.session.commit()

    def restore_snapshot(self, snapshot_id: int, components: Optional[List[str]] = None) -> Dict[str, bool]:
        """Restore workspace from snapshot"""
        snapshot = self.get_snapshot(snapshot_id)
        if not snapshot:
            raise ValueError(f"Snapshot {snapshot_id} not found")

        results = {}

        # Default: restore everything
        if not components:
            components = ["git", "editor", "terminal", "env"]

        if "git" in components and snapshot.git_branch:
            results["git"] = self._restore_git(snapshot)

        if "editor" in components and snapshot.editor_state:
            results["editor"] = self._restore_editor(snapshot)

        if "terminal" in components and snapshot.terminal_state:
            results["terminal"] = self._restore_terminal(snapshot)

        if "env" in components and snapshot.environment_vars:
            results["env"] = self._restore_env(snapshot)

        return results

    # Private methods for capturing state

    def _capture_git_state(self, project_path: str) -> Dict[str, Any]:
        """Capture git repository state"""
        try:
            repo = git.Repo(project_path)
            return {
                "branch": repo.active_branch.name,
                "commit": repo.head.commit.hexsha,
                "uncommitted": len(repo.index.diff(None)) > 0,
                "untracked": len(repo.untracked_files) > 0,
                "modified_files": [item.a_path for item in repo.index.diff(None)],
                "untracked_files": repo.untracked_files,
            }
        except Exception as e:
            return {"error": str(e)}

    def _capture_editor_state(self, project_path: str) -> Dict[str, Any]:
        """Capture VS Code state if available"""
        vscode_state = {}

        # Try to read VS Code workspace state
        workspace_storage = Path.home() / ".config" / "Code" / "User" / "workspaceStorage"

        if workspace_storage.exists():
            # This is simplified - actual implementation would parse VS Code storage
            vscode_state["workspace_detected"] = True
            vscode_state["project_path"] = project_path

        return vscode_state

    def _capture_terminal_state(self) -> Dict[str, Any]:
        """Capture terminal state"""
        try:
            cwd = os.getcwd()
            # Get shell history (last 10 commands)
            history_file = Path.home() / ".bash_history"
            history = []

            if history_file.exists():
                with open(history_file, "r") as f:
                    history = f.readlines()[-10:]

            return {
                "cwd": cwd,
                "history": [h.strip() for h in history],
            }
        except Exception as e:
            return {"error": str(e)}

    def _capture_env_vars(self) -> Dict[str, str]:
        """Capture safe environment variables"""
        safe_vars = [
            "PATH",
            "VIRTUAL_ENV",
            "NODE_ENV",
            "RUST_BACKTRACE",
            "EDITOR",
            "SHELL",
        ]

        return {key: os.environ.get(key, "") for key in safe_vars if key in os.environ}

    def _capture_processes(self) -> List[Dict[str, Any]]:
        """Capture running dev processes"""
        dev_processes = []

        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                # Filter for development-related processes
                name = proc.info["name"].lower()
                if any(keyword in name for keyword in ["node", "python", "rust", "cargo", "npm", "deno"]):
                    dev_processes.append({
                        "name": proc.info["name"],
                        "cmdline": " ".join(proc.info["cmdline"] or []),
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        return dev_processes[:10]  # Limit to 10 processes

    def _generate_ai_summary(self, snapshot: Snapshot) -> str:
        """Generate AI summary of snapshot (requires OpenAI API)"""
        try:
            from openai import OpenAI
            client = OpenAI()

            context = f"""
Project: {snapshot.project_path}
Branch: {snapshot.git_branch}
Editor State: {json.dumps(snapshot.editor_state, indent=2)}
Terminal: {json.dumps(snapshot.terminal_state, indent=2)}
"""

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that summarizes developer workspace snapshots.",
                    },
                    {
                        "role": "user",
                        "content": f"Summarize what the developer was working on:\n\n{context}",
                    },
                ],
                max_tokens=150,
            )

            return response.choices[0].message.content or "No summary available"
        except Exception as e:
            return f"Summary unavailable: {str(e)}"

    # Restore methods

    def _restore_git(self, snapshot: Snapshot) -> bool:
        """Restore git state"""
        try:
            repo = git.Repo(snapshot.project_path)
            if snapshot.git_branch:
                repo.git.checkout(snapshot.git_branch)
            return True
        except Exception as e:
            print(f"Git restore error: {e}")
            return False

    def _restore_editor(self, snapshot: Snapshot) -> bool:
        """Restore editor state (simplified)"""
        # In real implementation, would restore VS Code workspace
        return True

    def _restore_terminal(self, snapshot: Snapshot) -> bool:
        """Restore terminal state"""
        if snapshot.terminal_state and "cwd" in snapshot.terminal_state:
            try:
                os.chdir(snapshot.terminal_state["cwd"])
                return True
            except Exception:
                return False
        return False

    def _restore_env(self, snapshot: Snapshot) -> bool:
        """Restore environment variables"""
        if snapshot.environment_vars:
            for key, value in snapshot.environment_vars.items():
                os.environ[key] = value
            return True
        return False
