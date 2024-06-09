import argparse
import praw
import time
import ahocorasick
import threading
import signal
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.align import Align
from prawcore.exceptions import TooManyRequests

load_dotenv()

# Start the Reddit instance NOTE: you're going to need to register your own Reddit app!
reddit = praw.Reddit(
    client_id=os.getenv('REDDIT_CLIENT_ID'),
    client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
    user_agent=os.getenv('REDDIT_USER_AGENT'),
)

# Define the argument parser
parser = argparse.ArgumentParser(description="Monitor Reddit for keywords.")
parser.add_argument("--keywords", nargs='+', help="List of keywords to monitor", required=True)

# Parse the arguments
args = parser.parse_args()

# Define the subreddit to monitor, I just use "all" but you can be more specific
subreddit_name = 'all'
keywords = args.keywords

# Initialize Aho-Corasick, it super cool.
A = ahocorasick.Automaton()
for idx, keyword in enumerate(keywords):
    A.add_word(keyword.lower(), (idx, keyword))
A.make_automaton()

# Start Rich console for a more aesthetic output
console = Console()

# Flag to control the running state of threads
running = True

# Function to handle graceful shutdown, otherwise Ctrl+C only closes one thread at a time and its ugly
def signal_handler(sig, frame):
    global running
    console.print("[bold red]Shutting down gracefully...[/bold red]")
    running = False

# Register signal handler for SIGINT
signal.signal(signal.SIGINT, signal_handler)

# Function to check for keywords in a text using Aho-Corasick with word boundary checks
def contains_keywords(text):
    text = text.lower()
    for end_index, (idx, keyword) in A.iter(text):
        start_index = end_index - len(keyword) + 1
        before = start_index == 0 or not text[start_index - 1].isalnum()
        after = end_index + 1 == len(text) or not text[end_index + 1].isalnum()
        if before and after:
            return True
    return False

# Function to display a cool welcome banner (it is cool)
def display_banner():
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

# Function to monitor new submissions (reddit posts)
def monitor_submissions(subreddit):
    console.print("[bold green]:eyes: Starting to monitor submissions...[/bold green]")
    while running:
        try:
            for submission in subreddit.stream.submissions(skip_existing=True):
                if not running:
                    break
                if contains_keywords(submission.title) or contains_keywords(submission.selftext):
                    console.print(f"[bold yellow]Post:[/bold yellow] {submission.title}\n[bold blue]URL:[/bold blue] {submission.url}\n")
        except TooManyRequests as e:
            if not running:
                break
            retry_after = int(e.response.headers.get('Retry-After', 30))
            console.print(f"[bold red]:angry: Rate limit for submissions exceeded. Retrying in {retry_after} seconds...[/bold red]")
            time.sleep(retry_after)
            console.print("[bold green]:eyes: Resuming submissions monitoring...[/bold green]")
        except Exception as e:
            if not running:
                break
            console.print(f"[bold red]:angry: Error: {e}. Retrying in 30 seconds...[/bold red]")
            time.sleep(30)

# Function to monitor new comments
def monitor_comments(subreddit):
    console.print("[bold green]:eyes: Starting to monitor comments...[/bold green]")
    while running:
        try:
            for comment in subreddit.stream.comments(skip_existing=True):
                if not running:
                    break
                if contains_keywords(comment.body):
                    console.print(f"[bold yellow]Comment:[/bold yellow] {comment.body}\n[bold blue]URL:[/bold blue] https://www.reddit.com{comment.permalink}\n")
        except TooManyRequests as e:
            if not running:
                break
            retry_after = int(e.response.headers.get('Retry-After', 30))
            console.print(f"[bold red]:angry: Rate limit for comments exceeded. Retrying in {retry_after} seconds...[/bold red]")
            time.sleep(retry_after)
            console.print("[bold green]:eyes: Resuming comments monitoring...[/bold green]")
        except Exception as e:
            if not running:
                break
            console.print(f"[bold red]:angry: Error: {e}. Retrying in 30 seconds...[/bold red]")
            time.sleep(30)

if __name__ == "__main__":
    display_banner()

    subreddit = reddit.subreddit(subreddit_name)

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
        running = False
        submission_thread.join()
        comment_thread.join()
        console.print("[bold red]Shutdown complete.[/bold red]")
