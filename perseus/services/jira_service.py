"""Jira API integration service for enriching ticket data.

Uses centralized env variables exported from `perseus.env`.
"""
import re
import logging
from typing import Dict, Optional
from functools import lru_cache
from jira import JIRA
from perseus.services.config_service import ConfigService

class JiraService:
    """Fetches ticket data from Jira API with caching."""

    def __init__(self, config: ConfigService | None = None):
        cfg = config or ConfigService().config
        self.base_url = cfg.jira_base_url.rstrip("/")
        self.email = cfg.jira_email.strip('"').strip("'")
        self.api_token = cfg.jira_api_token.strip('"').strip("'")

        self.enabled = bool(self.base_url and self.email and self.api_token)
        self.jira = None

        if self.enabled:
            try:
                self.jira = JIRA(server=self.base_url, basic_auth=(self.email, self.api_token))
                logging.debug("Jira integration enabled")
            except Exception as e:
                logging.warning(f"Failed to initialize Jira client: {e}")
                self.enabled = False
        else:
            logging.debug("Jira integration disabled (JIRA_BASE_URL, JIRA_EMAIL, or JIRA_API_TOKEN not set)")

    @lru_cache(maxsize=128)
    def fetch_ticket(self, ticket_key: str) -> Optional[Dict]:
        """Fetch ticket data from Jira API with caching."""
        if not self.enabled or not self.jira:
            return None

        try:
            issue = self.jira.issue(ticket_key)

            return {
                "key": ticket_key,
                "title": issue.fields.summary,
                "status": issue.fields.status.name,
                "assignee": issue.fields.assignee.displayName if issue.fields.assignee else "Unassigned",
                "priority": issue.fields.priority.name if issue.fields.priority else "None",
                "url": f"{self.base_url}/browse/{ticket_key}"
            }
        except Exception as e:
            logging.warning(f"Failed to fetch Jira ticket {ticket_key}: {e}")
            return None

    def enrich_tickets(self, ticket_list: list[str]) -> list[Dict]:
        """Convert ticket strings to enriched ticket objects."""
        enriched = []

        for ticket in ticket_list:
            # Extract ticket key (e.g., "JIRA-123" from "JIRA-123: Description")
            match = re.match(r"([A-Z]+-\d+)", ticket)
            if not match:
                # Not a Jira ticket, keep as string
                enriched.append({"key": ticket, "title": ticket})
                continue

            ticket_key = match.group(1)
            ticket_data = self.fetch_ticket(ticket_key)

            if ticket_data:
                enriched.append(ticket_data)
            else:
                # Fallback if API fails
                enriched.append({"key": ticket_key, "title": ticket})

        return enriched
