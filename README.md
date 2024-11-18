# Hanafuda Auto Grow Bot

This project is designed to execute grow actions and track total points from a backend API. It interacts with a remote API to fetch information about available grow actions, execute them, and retrieve the updated **Total Points** after each grow action. The program continuously checks the status of the grow actions and performs them as long as they are available. It also ensures the **Total Points** are updated after each successful execution.

## Prerequisites

Before running the script, ensure you have the following:

- Python 3.11
- `requests` library
- `colorama` library
- `python-dotenv` library
- A `.env` file containing your API Key and Refresh Token

## Setup

1. Clone this repository or create a new directory to hold your project files.
2. Create a `.env` file in the root directory of your project and add the following content:

    ```
    API_KEY=your_api_key_here
    REFRESH_TOKEN=your_refresh_token_here
    ```

3. Install the required libraries using `pip`:

    ```bash
    pip install requests python-dotenv colorama
    ```

4. Update the `API_KEY` and `REFRESH_TOKEN` values in your `.env` file with the appropriate credentials.

## How It Works

1. **Fetching Grow Actions:**
   The script first checks the number of available grow actions by calling the `GetGardenForCurrentUser` API. If any grow actions are available, it proceeds to execute them.

2. **Executing Grow Actions:**
   For each available grow action, the script sends a request to execute the grow action using the `ExecuteGrowAction` mutation. After each execution, the script fetches and prints the updated **Total Points**.

3. **Total Points Update:**
   After each grow action, the script calls the `CurrentUserStatus` query to retrieve the updated **Total Points** and logs this value.

4. **Refreshing Tokens:**
   If the API Key has expired, the script uses the refresh token to obtain a new ID token to continue making authorized requests.

5. **Loop and Retry:**
   The script runs in a loop, checking every 5 minutes for available grow actions. If no actions are available, it waits for 5 minutes before checking again.

## Running the Script

To run the script, simply execute it from the command line:

```bash
python growhana.py
```
