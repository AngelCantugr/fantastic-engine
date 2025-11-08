#!/usr/bin/env python3
"""
Industry News Aggregator - Catalog Manager

This script helps manage the catalog of news searches and summaries.
It provides utilities for:
- Adding new entries to the catalog
- Searching the catalog
- Retrieving source material
- Rebuilding the catalog from files
- Generating reports
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import argparse


class CatalogManager:
    """Manages the news aggregator catalog."""

    def __init__(self, project_root: Optional[str] = None):
        """Initialize catalog manager."""
        if project_root is None:
            # Assume script is in scripts/ directory
            self.project_root = Path(__file__).parent.parent
        else:
            self.project_root = Path(project_root)

        self.catalog_path = self.project_root / "data" / "catalog.json"
        self.raw_dir = self.project_root / "data" / "raw"
        self.summaries_dir = self.project_root / "data" / "summaries"
        self.outputs_dir = self.project_root / "data" / "outputs"

        # Create directories if they don't exist
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.summaries_dir.mkdir(parents=True, exist_ok=True)
        self.outputs_dir.mkdir(parents=True, exist_ok=True)

        self.catalog = self._load_catalog()

    def _load_catalog(self) -> Dict:
        """Load the catalog from disk."""
        if self.catalog_path.exists():
            with open(self.catalog_path, 'r') as f:
                return json.load(f)
        else:
            return {
                "version": "1.0.0",
                "created": datetime.now().isoformat(),
                "description": "Catalog of all industry news searches and summaries",
                "entries": [],
                "topics": {}
            }

    def _save_catalog(self):
        """Save the catalog to disk."""
        with open(self.catalog_path, 'w') as f:
            json.dump(self.catalog, f, indent=2, sort_keys=False)

    def add_entry(
        self,
        topic: str,
        keywords: List[str],
        sources: Dict[str, str],
        summary_path: str,
        tags: List[str],
        relevance_score: float = 0.0,
        follow_up_questions: Optional[List[str]] = None,
        related_entries: Optional[List[str]] = None
    ) -> str:
        """Add a new entry to the catalog."""
        timestamp = datetime.now()
        entry_id = self._generate_entry_id(timestamp, topic)

        entry = {
            "id": entry_id,
            "timestamp": timestamp.isoformat(),
            "topic": topic,
            "keywords": keywords,
            "sources": sources,
            "summary": summary_path,
            "tags": tags,
            "relevance_score": relevance_score,
            "follow_up_questions": follow_up_questions or [],
            "related_entries": related_entries or []
        }

        self.catalog["entries"].append(entry)

        # Update topics index
        for tag in tags:
            if tag not in self.catalog["topics"]:
                self.catalog["topics"][tag] = []
            self.catalog["topics"][tag].append(entry_id)

        self._save_catalog()
        return entry_id

    def _generate_entry_id(self, timestamp: datetime, topic: str) -> str:
        """Generate a unique entry ID."""
        slug = topic.lower().replace(" ", "-")[:30]
        return f"{timestamp.strftime('%Y-%m-%d-%H%M%S')}-{slug}"

    def search(
        self,
        query: Optional[str] = None,
        tags: Optional[List[str]] = None,
        since: Optional[str] = None,
        min_relevance: float = 0.0
    ) -> List[Dict]:
        """Search the catalog."""
        results = self.catalog["entries"]

        if query:
            query_lower = query.lower()
            results = [
                e for e in results
                if query_lower in e["topic"].lower()
                or any(query_lower in k.lower() for k in e["keywords"])
            ]

        if tags:
            results = [
                e for e in results
                if any(tag in e["tags"] for tag in tags)
            ]

        if since:
            since_dt = datetime.fromisoformat(since)
            results = [
                e for e in results
                if datetime.fromisoformat(e["timestamp"]) >= since_dt
            ]

        if min_relevance > 0:
            results = [
                e for e in results
                if e["relevance_score"] >= min_relevance
            ]

        return sorted(results, key=lambda x: x["timestamp"], reverse=True)

    def get_entry(self, entry_id: str) -> Optional[Dict]:
        """Get a specific entry by ID."""
        for entry in self.catalog["entries"]:
            if entry["id"] == entry_id:
                return entry
        return None

    def get_sources(self, entry_id: str) -> Dict[str, Path]:
        """Get source file paths for an entry."""
        entry = self.get_entry(entry_id)
        if not entry:
            return {}

        sources = {}
        for source_type, relative_path in entry["sources"].items():
            full_path = self.project_root / relative_path
            if full_path.exists():
                sources[source_type] = full_path

        return sources

    def get_summary(self, entry_id: str) -> Optional[str]:
        """Get the summary content for an entry."""
        entry = self.get_entry(entry_id)
        if not entry:
            return None

        summary_path = self.project_root / entry["summary"]
        if summary_path.exists():
            with open(summary_path, 'r') as f:
                return f.read()
        return None

    def rebuild_from_files(self):
        """Rebuild catalog by scanning data directories."""
        print("Rebuilding catalog from files...")
        new_entries = []

        # Scan summaries directory
        for summary_file in self.summaries_dir.glob("*.md"):
            # Try to extract metadata from filename
            # Format: YYYY-MM-DD-HHMMSS-topic-slug.md
            filename = summary_file.stem
            parts = filename.split("-")

            if len(parts) >= 4:
                # Check if this entry already exists
                existing = any(e["summary"].endswith(summary_file.name) for e in self.catalog["entries"])
                if not existing:
                    # Try to find corresponding raw files
                    raw_files = {}
                    for raw_file in self.raw_dir.glob(f"{filename}*.json"):
                        if "brave" in raw_file.name:
                            raw_files["brave"] = str(raw_file.relative_to(self.project_root))
                        elif "perplexity" in raw_file.name:
                            raw_files["perplexity"] = str(raw_file.relative_to(self.project_root))

                    # Create entry
                    topic = " ".join(parts[3:]).replace("-", " ").title()
                    new_entry = {
                        "id": filename,
                        "timestamp": f"{parts[0]}-{parts[1]}-{parts[2]}T{parts[3][:2]}:{parts[3][2:4]}:{parts[3][4:6]}Z",
                        "topic": topic,
                        "keywords": [],
                        "sources": raw_files,
                        "summary": str(summary_file.relative_to(self.project_root)),
                        "tags": [],
                        "relevance_score": 0.0,
                        "follow_up_questions": [],
                        "related_entries": []
                    }
                    new_entries.append(new_entry)

        if new_entries:
            self.catalog["entries"].extend(new_entries)
            self._save_catalog()
            print(f"Added {len(new_entries)} new entries to catalog")
        else:
            print("No new entries found")

    def list_topics(self) -> Dict[str, int]:
        """List all topics and their entry counts."""
        return {
            topic: len(entry_ids)
            for topic, entry_ids in self.catalog["topics"].items()
        }

    def generate_report(self, output_file: Optional[str] = None) -> str:
        """Generate a markdown report of catalog contents."""
        report = ["# Industry News Aggregator - Catalog Report\n"]
        report.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append(f"**Total Entries**: {len(self.catalog['entries'])}\n")

        # Topics summary
        report.append("\n## Topics\n")
        topics = self.list_topics()
        for topic, count in sorted(topics.items(), key=lambda x: x[1], reverse=True):
            report.append(f"- **{topic}**: {count} entries")

        # Recent entries
        report.append("\n## Recent Entries (Last 10)\n")
        recent = sorted(self.catalog["entries"], key=lambda x: x["timestamp"], reverse=True)[:10]
        for entry in recent:
            report.append(f"\n### {entry['topic']}")
            report.append(f"- **ID**: `{entry['id']}`")
            report.append(f"- **Date**: {entry['timestamp'][:10]}")
            report.append(f"- **Tags**: {', '.join(entry['tags'])}")
            report.append(f"- **Relevance**: {entry['relevance_score']}/10")

        report_text = "\n".join(report)

        if output_file:
            output_path = Path(output_file)
            with open(output_path, 'w') as f:
                f.write(report_text)
            print(f"Report saved to {output_path}")

        return report_text


def main():
    """CLI interface for catalog manager."""
    parser = argparse.ArgumentParser(description="Industry News Aggregator - Catalog Manager")
    parser.add_argument("--project-root", help="Project root directory")

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search the catalog")
    search_parser.add_argument("--query", help="Search query")
    search_parser.add_argument("--tags", nargs="+", help="Filter by tags")
    search_parser.add_argument("--since", help="Filter by date (ISO format)")
    search_parser.add_argument("--min-relevance", type=float, default=0.0, help="Minimum relevance score")

    # Get command
    get_parser = subparsers.add_parser("get", help="Get entry details")
    get_parser.add_argument("entry_id", help="Entry ID")
    get_parser.add_argument("--sources", action="store_true", help="Show source files")
    get_parser.add_argument("--summary", action="store_true", help="Show summary content")

    # Rebuild command
    subparsers.add_parser("rebuild", help="Rebuild catalog from files")

    # Topics command
    subparsers.add_parser("topics", help="List all topics")

    # Report command
    report_parser = subparsers.add_parser("report", help="Generate catalog report")
    report_parser.add_argument("--output", help="Output file path")

    args = parser.parse_args()

    manager = CatalogManager(args.project_root)

    if args.command == "search":
        results = manager.search(
            query=args.query,
            tags=args.tags,
            since=args.since,
            min_relevance=args.min_relevance
        )
        print(f"Found {len(results)} results:\n")
        for entry in results:
            print(f"[{entry['timestamp'][:10]}] {entry['topic']} (ID: {entry['id']})")
            print(f"  Tags: {', '.join(entry['tags'])}")
            print(f"  Relevance: {entry['relevance_score']}/10\n")

    elif args.command == "get":
        entry = manager.get_entry(args.entry_id)
        if entry:
            print(json.dumps(entry, indent=2))

            if args.sources:
                print("\nSource Files:")
                sources = manager.get_sources(args.entry_id)
                for source_type, path in sources.items():
                    print(f"  {source_type}: {path}")

            if args.summary:
                print("\nSummary:")
                print(manager.get_summary(args.entry_id))
        else:
            print(f"Entry not found: {args.entry_id}")

    elif args.command == "rebuild":
        manager.rebuild_from_files()

    elif args.command == "topics":
        topics = manager.list_topics()
        print("Topics:")
        for topic, count in sorted(topics.items(), key=lambda x: x[1], reverse=True):
            print(f"  {topic}: {count} entries")

    elif args.command == "report":
        report = manager.generate_report(args.output)
        if not args.output:
            print(report)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
