# FacebookPostsScraper

> ## ⚠️ Unmaintained — this scraper no longer works
>
> **Facebook broke it, and it cannot be patched.** Verified against Facebook as of
> September 2026: the code fails on its very first request, before your credentials
> are even sent.
>
> This project worked by sending a **Nokia C3 User-Agent** so that Facebook would
> serve the old JavaScript-free mobile HTML, which was simple enough to parse. All
> three pillars of that approach are now gone:
>
> 1. **The legacy User-Agent is blocked.** `m.facebook.com` and `mbasic.facebook.com`
>    both answer with a 3.7 KB error page — *"Facebook is not available on this
>    device"* — served with **HTTP 200**, so the request looks successful and the
>    failure only surfaces later as a confusing `AttributeError`.
> 2. **The login form is gone.** The six hidden fields `login()` scrapes (`lsd`,
>    `jazoest`, `m_ts`, `li`, `try_number`, `unrecognized_tries`) no longer exist —
>    not even with a modern User-Agent. Login is a React app now.
> 3. **The post selectors match nothing.** `.storyStream > div`, `#recent > div > div > div`
>    and `#m_group_stories_container > div > div` all return zero nodes.
>
> Running the example raises:
>
> ```
> File "FacebookPostsScraper.py", line 75, in login
>     lsd = soup.find("input", {"name": "lsd"}).get("value")
> AttributeError: 'NoneType' object has no attribute 'get'
> ```
>
> Separately, `requirements.txt` no longer installs on Python 3.12+: `numpy==1.19.0`
> needs `distutils`, which was removed from the standard library.
>
> **No fix is planned.** Restoring this would mean a fundamentally different project,
> and automated credential login now also runs into 2FA and Facebook's security
> checkpoints. If you need Facebook data today, use the official
> [Graph API](https://developers.facebook.com/docs/graph-api/). The code below is kept
> for reference and as a snapshot of a technique that worked from 2020 to roughly 2023.

Scraper for posts in Facebook user profiles, pages and groups.

Extracts list of dicts with:

| params         | description |
| -------------- | ----------- |
| published      | Formatted datetime of published |
| description    | Post text content |
| images         | List of images in posts |
| post_url       | The unique post url |
| external_links | External links found in description |
| like_url       | The Like url |

## Installation

1.Get [Python](https://www.python.org/downloads/) (recommended Python 3.7+)

2.Clone or download this repository

```shell script
git clone https://github.com/adeoy/FacebookPostsScraper.git
```

3.Install the Python requirements

```shell script
pip install -r requirements.txt
```

4.Follow the examples.

## Description

### The FacebookPostsScraper Class

Constructor params:

| param         | description |
| ------------- | ----------- |
| email | Your email to access Facebook |
| password | Your password to access Facebook |
| post_url_text | This is the text in the Url that opens the posts in mobile version, use when your Facebook isn't in English |

When instantiate object it autologs in, and sets the session and save a cookie file for future use.

### Methods

`get_posts_from_profile`

params:

- profile url

return:

- list of dicts with the data described above

`get_posts_from_list`

params:

- list of profile urls

return:

- list of list of dicts with the data described above

## Examples

### Example with single url

```python
from FacebookPostsScraper import FacebookPostsScraper as Fps
from pprint import pprint as pp

# Enter your Facebook email and password
email = 'YOUR_EMAIL'
password = 'YOUR_PASWORD'

# Instantiate an object
fps = Fps(email, password, post_url_text='Full Story')

# Example with single profile
single_profile = 'https://www.facebook.com/BillGates'
data = fps.get_posts_from_profile(single_profile)
pp(data)

fps.posts_to_csv('my_posts')  # You can export the posts as CSV document
# fps.posts_to_excel('my_posts')  # You can export the posts as Excel document
# fps.posts_to_json('my_posts')  # You can export the posts as JSON document
```

### Example with multiple urls

```python
from FacebookPostsScraper import FacebookPostsScraper as Fps
from pprint import pprint as pp

# Enter your Facebook email and password
email = 'YOUR_EMAIL'
password = 'YOUR_PASWORD'

# Instantiate an object
fps = Fps(email, password, post_url_text='Full Story')

# Example with multiple profiles
profiles = [
    'https://www.facebook.com/zuck', # User profile
    'https://www.facebook.com/thepracticaldev', # Facebook page
    'https://www.facebook.com/groups/python' # Facebook group
]
data = fps.get_posts_from_list(profiles)
pp(data)

fps.posts_to_csv('my_posts')  # You can export the posts as CSV document
# fps.posts_to_excel('my_posts')  # You can export the posts as Excel document
# fps.posts_to_json('my_posts')  # You can export the posts as JSON document
```

## Questions

Please be free of ask anything in you want in the issue sections.
