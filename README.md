# RedRip
A Reddit image ripper that works with imgur, gfycat and any direct URLs


# Setup

```py
pip install -r requirements.txt
```

[Register an imgur client](https://api.imgur.com/oauth2/addclient)

Copy the client ID and client secret into ``Config.ini``

# Usage

```
RedRip.py [-h] -r REDDIT [-a [AMOUNT]]
          [-s [{hot,new,rising,controversial,top,guilded}]] [-l [LAST]]

Fetches images from subreddits

optional arguments:
  -h, --help            show this help message and exit
  -a [AMOUNT], --amount [AMOUNT]
                        The amount of submissions to crawl
  -s [{hot,new,rising,controversial,top,guilded}], --sort [{hot,new,rising,controversial,top,guilded}]
                        What to sort by
  -l [LAST], --last [LAST]
                        The post ID to pull after

required named arguments:
  -r REDDIT, --reddit REDDIT
                        the subreddit to crawl
```