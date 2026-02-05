# Personal AI Employee - Hackathon 0

This project implements a "Digital FTE" (Full-Time Equivalent) as described in the Hackathon0.md document. The AI Employee operates as an autonomous agent using Claude Code as the reasoning engine and Obsidian as the management dashboard.

## Architecture Overview

The system follows a Perception → Reasoning → Action pattern:

- **Perception**: Watcher scripts monitor various inputs (Gmail, WhatsApp, filesystem)
- **Reasoning**: Claude Code processes information and makes decisions
- **Action**: MCP servers perform external actions (sending emails, making payments, etc.)

## Project Structure

The project is organized into three tiers representing increasing levels of sophistication:

### Bronze Tier (`/bronze`)
- Basic Obsidian vault with Dashboard.md and Company_Handbook.md
- File system watcher for monitoring
- Claude Code integration with vault
- Basic folder structure: /Inbox, /Needs_Action, /Done
- Core Agent Skills for file management and basic operations

### Silver Tier (`/silver`)
- All Bronze features plus:
- Multiple watcher scripts (Gmail, WhatsApp)
- LinkedIn posting capabilities
- Planning engine for multi-step tasks
- Human-in-the-loop approval workflows
- Scheduling capabilities

### Gold Tier (`/gold`)
- All Silver features plus:
- Full cross-domain integration
- Odoo accounting system integration
- Multi-platform social media management
- Business audit and CEO briefing generation
- Comprehensive error recovery
- Ralph Wiggum persistent loops

## Setup Instructions

1. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up Claude Code with appropriate MCP servers

3. Configure credentials for external services (Gmail, social media, etc.)

4. Run the orchestrator:
   ```
   python orchestrator.py /path/to/vault
   ```

## Security Considerations

- Store credentials securely using environment variables or secure credential managers
- Implement proper approval workflows for sensitive actions
- Maintain comprehensive audit logs
- Follow the Human-in-the-Loop pattern for critical operations

## Skills Directory

Each tier has its own `.claude/skills/` directory containing Agent Skills that implement the various capabilities of the AI Employee. These skills follow the patterns described in the hackathon document and enable the AI to perform complex operations while maintaining safety and control.