# MENSHUN

![menshun](https://github.com/dansholds/menshun/assets/25537601/d97368ed-91e0-43d1-82d7-6b7c8301ecf3)

**NOTE**: I still need to fine-tune the rate limiting, I don't do exponential back offs as it doesn't seem like its needed so if we hit a rate limit it will pause for 30 seconds and go again. Feel free to submit a PR to improve it!

A super cool Python script to monitor Reddit posts and comments for specified keywords using the PRAW (Python Reddit API Wrapper) and Aho-Corasick algorithm for efficient keyword matching. The script also provides aesthetic output using the Rich library.

Shout out to https://f5bot.com for the inspiration especially when using Aho-Corasick!

## Table of Contents

- [Description](#description)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Description

This project monitors Reddit for keywords in new submissions and comments in real time. It utilises the Aho-Corasick algorithm for fast keyword searching and the Rich library for beautiful console output. The script also supports graceful shutdown and handles Reddit's rate limits as both can ruin the vibe.

## Features

- Monitors multiple keywords in Reddit posts and comments.
- Utilises Aho-Corasick algorithm for efficient keyword matching.
- Handles Reddit API rate limits.
- Looks good doing it with the [Rich library](https://github.com/Textualize/rich).
- Supports graceful shutdown on receiving a SIGINT signal (Ctrl+C).

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/dansholds/menshun.git
    cd menshun
    ```

2. **Create a virtual environment (optional but recommended):**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install the required dependencies:**

    ```bash
    pip3 install -r requirements.txt
    ```

4. **Set up environment variables:**

    Create a `.env` file in the project directory with your Reddit app credentials:

    ```env
    REDDIT_CLIENT_ID=your_client_id
    REDDIT_CLIENT_SECRET=your_client_secret
    REDDIT_USER_AGENT=your_user_agent
    ```

    You can register a Reddit app to get these credentials at [Reddit Apps](https://www.reddit.com/prefs/apps). It's super quick and free!

## Usage

1. **Run the script:**

    ```bash
    python3 menshun.py --keywords keyword1 keyword2 keyword3
    ```

    Replace `keyword1`, `keyword2`, `keyword3`, etc., with the actual keywords you want to monitor.

2. **Example command:**

    ```bash
    python menshun.py --keywords python programming reddit #(don't actually use reddit as a keyword unless you want your terminal slammed with crap lol)
    ```

3. **Graceful shutdown:**

    To stop the script, press `Ctrl+C`. The script will handle the signal and shut down gracefully.

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Make your changes.
4. Commit your changes with a descriptive commit message.
5. Push your changes to your fork.
6. Create a pull request to the main repository.
7. profit

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or suggestions, please contact:

- GitHub: [dansholds](https://github.com/dansholds)
- X: https://x.com/0xT33m0
