# orchestrator.py
import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime

class Orchestrator:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.tier_names = ['bronze', 'silver', 'gold']

        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def ensure_needs_action_dirs(self):
        """Ensure that each tier has a Needs_Action directory"""
        for tier in self.tier_names:
            tier_path = self.vault_path / tier
            needs_action_dir = tier_path / 'Needs_Action'

            if not needs_action_dir.exists():
                needs_action_dir.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Created Needs_Action directory: {needs_action_dir}")

    def scan_needs_action(self):
        """Scan all tier directories for new tasks in their Needs_Action folders"""
        all_task_files = []

        for tier in self.tier_names:
            tier_path = self.vault_path / tier
            needs_action_dir = tier_path / 'Needs_Action'

            # Create the directory if it doesn't exist
            if not needs_action_dir.exists():
                needs_action_dir.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Created Needs_Action directory: {needs_action_dir}")

            # Scan for .md files in the current tier's Needs_Action directory
            tier_task_files = list(needs_action_dir.glob("*.md"))
            all_task_files.extend(tier_task_files)

            if tier_task_files:
                self.logger.info(f"Found {len(tier_task_files)} tasks in {tier}/Needs_Action")

        return all_task_files

    def process_task(self, task_file: Path):
        """Process a single task file"""
        self.logger.info(f"Processing task: {task_file.name}")

        # Read the task file
        content = task_file.read_text(encoding='utf-8')

        # Determine the tier based on the task file's location
        tier_path_parts = task_file.parts
        tier = 'unknown'
        for t in self.tier_names:
            if t in tier_path_parts:
                tier = t
                break

        # Create the corresponding directories in the same tier
        tier_base_path = task_file.parent.parent  # Go up from Needs_Action to tier directory
        plans_dir = tier_base_path / 'Plans'
        done_dir = tier_base_path / 'Done'

        # Create directories if they don't exist
        plans_dir.mkdir(exist_ok=True)
        done_dir.mkdir(exist_ok=True)

        # Create a plan file based on the task
        plan_file = plans_dir / f"PLAN_{task_file.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        plan_content = f"""---
created: {datetime.now().isoformat()}
status: in_progress
related_task: {task_file.name}
tier: {tier}
---

# Plan for {task_file.name}

## Objective
Process the task described in {task_file.name}

## Steps
- [ ] Analyze the task requirements
- [ ] Determine necessary actions
- [ ] Execute required operations
- [ ] Update dashboard with results
- [ ] Mark task as completed

## Progress Tracking
Started at: {datetime.now().isoformat()}
"""
        plan_file.write_text(plan_content)

        self.logger.info(f"Created plan: {plan_file.name}")

    def move_to_done(self, task_file: Path):
        """Move a processed task to the Done directory in the same tier"""
        # Determine the tier and move to the corresponding Done directory
        tier_base_path = task_file.parent.parent  # Go up from Needs_Action to tier directory
        done_dir = tier_base_path / 'Done'

        # Create Done directory if it doesn't exist
        done_dir.mkdir(exist_ok=True)

        done_file = done_dir / task_file.name
        task_file.rename(done_file)
        self.logger.info(f"Moved {task_file.name} to {done_dir.relative_to(self.vault_path)}")

    def run_cycle(self):
        """Run one cycle of the orchestrator"""
        self.logger.info("Starting orchestrator cycle...")

        # Ensure all tier directories have Needs_Action folders
        self.ensure_needs_action_dirs()

        # Scan for new tasks across all tiers
        task_files = self.scan_needs_action()

        if not task_files:
            self.logger.info("No new tasks found across all tiers.")
            return

        self.logger.info(f"Found {len(task_files)} tasks to process across all tiers")

        # Process each task
        for task_file in task_files:
            try:
                self.process_task(task_file)
                self.move_to_done(task_file)
            except Exception as e:
                self.logger.error(f"Error processing {task_file.name}: {e}")

        self.logger.info("Orchestrator cycle completed.")

    def run_forever(self, interval: int = 60):
        """Run the orchestrator continuously"""
        self.logger.info("Starting orchestrator in continuous mode...")

        while True:
            try:
                self.run_cycle()
                time.sleep(interval)
            except KeyboardInterrupt:
                self.logger.info("Orchestrator stopped by user.")
                break
            except Exception as e:
                self.logger.error(f"Orchestrator error: {e}")
                time.sleep(interval)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python orchestrator.py <vault_path>")
        sys.exit(1)

    vault_path = sys.argv[1]
    orchestrator = Orchestrator(vault_path)

    # Run once if --once flag is provided, otherwise run continuously
    if '--once' in sys.argv:
        orchestrator.run_cycle()
    else:
        orchestrator.run_forever()