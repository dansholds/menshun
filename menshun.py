"""Live Reddit Monitoring for chosen keyword."""
import argparse
import os
import signal
import time
import threading
import praw
import ahocorasick # pylint: disable=no-member
from dotenv import load_dotenv
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from prawcore.exceptions import TooManyRequests

load_dotenv()

# Start the Reddit instance NOTE: you're going to need to register your own Reddit app!
reddit = praw.Reddit(
    client_id=os.getenv('REDDIT_CLIENT_ID'),
    client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
    user_agent=os.getenv('REDDIT_USER_AGENT'),
)

# Define the argument parser.
parser = argparse.ArgumentParser(description="Monitor Reddit for keywords.")
parser.add_argument("--keywords", nargs='+', help="List of keywords to monitor", required=True)

# Parse the arguments.
args = parser.parse_args()

# Define the subreddit to monitor, I just use "all" but you can be more specific.
SUBREDDIT_NAME = 'all'
keywords = args.keywords

# Initialize Aho-Corasick, its super cool.
A = ahocorasick.Automaton()
for idx, keyword in enumerate(keywords):
    A.add_word(keyword.lower(), (idx, keyword))
A.make_automaton()

# Start Rich console for a more aesthetic output
console = Console()

# Flag to control the running state of threads
RUNNING = True

# Function to handle graceful shutdown, otherwise Ctrl+C only
# closes one thread at a time and its ugly
def signal_handler(_, __): # noqa: F841
    """Allow script to shutdown gracefully"""
    global RUNNING
    console.print("[bold red]Shutting down gracefully...[/bold red]")
    RUNNING = False

# Register signal handler for SIGINT
signal.signal(signal.SIGINT, signal_handler)

def contains_keywords(text):
    """Checks text for keyword"""
    text = text.lower()
    for end_index, (idx, keyword) in A.iter(text):
        start_index = end_index - len(keyword) + 1
        before = start_index == 0 or not text[start_index - 1].isalnum()
        after = end_index + 1 == len(text) or not text[end_index + 1].isalnum()
        if before and after:
            return True
    return False

def display_banner():
    """Function to display a cool welcome banner (it is cool)"""
    banner_text = """
░▒▓██████████████▓▒░░▒▓████████▓▒░▒▓███████▓▒░ ░▒▓███████▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓███████▓▒░  
░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓██████▓▒░ ░▒▓█▓▒░░▒▓█▓▒░░▒▓██████▓▒░░▒▓████████▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓████████▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓███████▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓██████▓▒░░▒▓█▓▒░░▒▓█▓▒░ 
    """
    console.print(Panel(Text(banner_text, justify="center", style="bold cyan"), border_style="bold white"))

def monitor_submissions(subreddit):
    """# Function to monitor new submissions (reddit posts)
"""
    console.print("[bold green]:eyes: Starting to monitor submissions...[/bold green]")
    while RUNNING:
        try:
            for submission in subreddit.stream.submissions(skip_existing=True):
                if not RUNNING:
                    break
                if contains_keywords(submission.title) or contains_keywords(submission.selftext):
                    console.print(f"[bold yellow]Post:[/bold yellow] {submission.title}\n[bold blue]URL:[/bold blue] {submission.url}\n")
        except TooManyRequests as e:
            if not RUNNING:
                break
            retry_after = int(e.response.headers.get('Retry-After', 30))
            console.print(f"[bold red]:angry: Rate limit for submissions exceeded. Retrying in {retry_after} seconds...[/bold red]")
            time.sleep(retry_after)
            console.print("[bold green]:eyes: Resuming submissions monitoring...[/bold green]")
        except Exception as e:
            if not RUNNING:
                break
            console.print(f"[bold red]:angry: Error: {e}. Retrying in 30 seconds...[/bold red]")
            time.sleep(30)

def monitor_comments(subreddit):
    """# Function to monitor new comments
"""
    console.print("[bold green]:eyes: Starting to monitor comments...[/bold green]")
    while RUNNING:
        try:
            for comment in subreddit.stream.comments(skip_existing=True):
                if not RUNNING:
                    break
                if contains_keywords(comment.body):
                    console.print(f"[bold yellow]Comment:[/bold yellow] {comment.body}\n[bold blue]URL:[/bold blue] https://www.reddit.com{comment.permalink}\n")
        except TooManyRequests as e:
            if not RUNNING:
                break
            retry_after = int(e.response.headers.get('Retry-After', 30))
            console.print(f"[bold red]:angry: Rate limit for comments exceeded. Retrying in {retry_after} seconds...[/bold red]")
            time.sleep(retry_after)
            console.print("[bold green]:eyes: Resuming comments monitoring...[/bold green]")
        except Exception as e:
            if not RUNNING:
                break
            console.print(f"[bold red]:angry: Error: {e}. Retrying in 30 seconds...[/bold red]")
            time.sleep(30)

if __name__ == "__main__":
    display_banner()

    subreddit = reddit.subreddit(SUBREDDIT_NAME)

    # Create threads for post and comment monitoring
    submission_thread = threading.Thread(target=monitor_submissions, args=(subreddit,))
    comment_thread = threading.Thread(target=monitor_comments, args=(subreddit,))

    # Start the threads
    submission_thread.start()
    comment_thread.start()

    # Wait for threads to finish
    try:
        submission_thread.join()
        comment_thread.join()
    except KeyboardInterrupt:
        console.print("[bold red]Shutting down... Please wait for threads to finish.[/bold red]")
        RUNNING = False
        submission_thread.join()
        comment_thread.join()
        console.print("[bold red]Shutdown complete.[/bold red]")
