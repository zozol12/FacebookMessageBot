# Facebook Messaging Bot
Facebook bot made to automate sending messages to users.\
Made using Selenium. **It uses Google Chrome only.**\
It uses normal facebook accounts\
You can login using: **Login & Password** or **Cookies**\
Bot is really simple and may be unstable.\
**Tested only on Windows, Python 3.9**
# Features
- Login via login/pass or cookies,
- Send message to facebook user using his user id,
- You can use [c3c FbState Utility]() to export cookies (anything else should work too)
- And that's it for now.

# Examples
1. Example usage

- Using **Credentials**
```python
import time
from FbBot import FbBot

if __name__ == '__main__':
    # Create bot using Login and Password
    fb_bot = FbBot.from_credentials("example@example.com", "password", headless=False)
    # Login
    fb_bot.login()
    while True:
        time.sleep(5)
        # Send message to user with uid 000000000000000
        fb_bot.send_message("000000000000000", "Hello man :ooo")
```
- Using **Cookies**
```python
import time
import json
from FbBot import FbBot

# Example helping function to get cookies from json file
def load_cookies(filename):
    try:
        # Load cookies from file
        with open(filename) as f:
            return json.load(f)
    except FileNotFoundError:
        return None

if __name__ == '__main__':
    # Get Cookies from file as list
    cookies = load_cookies("Cookies.json")
    # Create bot using Cookies
    fb_bot = FbBot.from_cookies(cookies, headless=False)
    # Login
    fb_bot.login()
    # Example message loop
    while True:
        time.sleep(5)
        # Send message to user with uid 000000000000000
        fb_bot.send_message("000000000000000", "Hello man :ooo")
```
# Installation
Python 3.9 required
# TODO
- Queue for messages,
- Better logging,
- Scraping users from facebook groups,
- Asynchronous methods
- **...**