import os
from dotenv import load_dotenv

load_dotenv()

LOG_LEVEL=os.environ.get("LOG_LEVEL", "DEBUG") # https://docs.python.org/3/library/logging.html#levels

# Jira
JIRA_BASE_URL=os.environ.get("JIRA_BASE_URL", "")
JIRA_EMAIL=os.environ.get("JIRA_EMAIL", "")
JIRA_API_TOKEN=os.environ.get("JIRA_API_TOKEN", "")
