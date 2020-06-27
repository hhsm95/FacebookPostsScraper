import requests
from bs4 import BeautifulSoup
import pickle
import os
from urllib.parse import urlparse, unquote
from urllib.parse import parse_qs
import pandas as pd
import json


class FacebookPostsScraper:

    # We need the email and password to access Facebook, and optionally the text in the Url that identifies the "view full post".
    def __init__(self, email, password, post_url_text='Full Story'):
        self.email = email
        self.password = password
        self.headers = {  # This is the important part: Nokia C3 User Agent
            'User-Agent': 'NokiaC3-00/5.0 (07.20) Profile/MIDP-2.1 Configuration/CLDC-1.1 Mozilla/5.0 AppleWebKit/420+ (KHTML, like Gecko) Safari/420+'
        }
        self.session = requests.session()  # Create the session for the next requests
        self.cookies_path = 'session_facebook.cki'  # Give a name to store the session in a cookie file.

        # At certain point, we need find the text in the Url to point the url post, in my case, my Facebook is in
        # English, this is why it says 'Full Story', so, you need to change this for your language.
        # Some translations:
        # - English: 'Full Story'
        # - Spanish: 'Historia completa'
        self.post_url_text = post_url_text

        # Evaluate if NOT exists a cookie file, if NOT exists the we make the Login request to Facebook,
        # else we just load the current cookie to maintain the older session.
        if self.new_session():
            self.login()

        self.posts = []  # Store the scraped posts

    # We need to check if we already have a session saved or need to log to Facebook
    def new_session(self):
        if not os.path.exists(self.cookies_path):
            return True

        f = open(self.cookies_path, 'rb')
        cookies = pickle.load(f)
        self.session.cookies = cookies
        return False

    # Utility function to make the requests and convert to soup object if necessary
    def make_request(self, url, method='GET', data=None, is_soup=True):
        if len(url) == 0:
            raise Exception(f'Empty Url')

        if method == 'GET':
            resp = self.session.get(url, headers=self.headers)
        elif method == 'POST':
            resp = self.session.post(url, headers=self.headers, data=data)
        else:
            raise Exception(f'Method [{method}] Not Supported')

        if resp.status_code != 200:
            raise Exception(f'Error [{resp.status_code}] > {url}')

        if is_soup:
            return BeautifulSoup(resp.text, 'lxml')
        return resp

    # The first time we login
    def login(self):
        # Get the content of HTML of mobile Login Facebook page
        url_home = "https://m.facebook.com/"
        soup = self.make_request(url_home)
        if soup is None:
            raise Exception("Couldn't load the Login Page")

        # Here we need to extract this tokens from the Login Page
        lsd = soup.find("input", {"name": "lsd"}).get("value")
        jazoest = soup.find("input", {"name": "jazoest"}).get("value")
        m_ts = soup.find("input", {"name": "m_ts"}).get("value")
        li = soup.find("input", {"name": "li"}).get("value")
        try_number = soup.find("input", {"name": "try_number"}).get("value")
        unrecognized_tries = soup.find("input", {"name": "unrecognized_tries"}).get("value")

        # This is the url to send the login params to Facebook
        url_login = "https://m.facebook.com/login/device-based/regular/login/?refsrc=https%3A%2F%2Fm.facebook.com%2F&lwv=100&refid=8"
        payload = {
            "lsd": lsd,
            "jazoest": jazoest,
            "m_ts": m_ts,
            "li": li,
            "try_number": try_number,
            "unrecognized_tries": unrecognized_tries,
            "email": self.email,
            "pass": self.password,
            "login": "Iniciar sesión",
            "prefill_contact_point": "",
            "prefill_source": "",
            "prefill_type": "",
            "first_prefill_source": "",
            "first_prefill_type": "",
            "had_cp_prefilled": "false",
            "had_password_prefilled": "false",
            "is_smart_lock": "false",
            "_fb_noscript": "true"
        }
        soup = self.make_request(url_login, method='POST', data=payload, is_soup=True)
        if soup is None:
            raise Exception(f"The login request couldn't be made: {url_login}")

        redirect = soup.select_one('a')
        if not redirect:
            raise Exception("Please log in desktop/mobile Facebook and change your password")

        url_redirect = redirect.get('href', '')
        resp = self.make_request(url_redirect)
        if resp is None:
            raise Exception(f"The login request couldn't be made: {url_redirect}")

        # Finally we get the cookies from the session and save it in a file for future usage
        cookies = self.session.cookies
        f = open(self.cookies_path, 'wb')
        pickle.dump(cookies, f)

        return {'code': 200}

    # Scrap a list of profiles
    def get_posts_from_list(self, profiles):
        data = []
        n = len(profiles)

        for idx in range(n):
            profile = profiles[idx]
            print(f'{idx + 1}/{n}. {profile}')

            posts = self.get_posts_from_profile(profile)
            data.append(posts)

        return data

    # This is the extraction point!
    def get_posts_from_profile(self, url_profile):
        # Prepare the Url to point to the posts feed
        if "www." in url_profile: url_profile = url_profile.replace('www.', 'm.')
        if 'v=timeline' not in url_profile:
            if '?' in url_profile:
                url_profile = f'{url_profile}&v=timeline'
            else:
                url_profile = f'{url_profile}?v=timeline'

        is_group = '/groups/' in url_profile

        # Make a simple GET request
        soup = self.make_request(url_profile)
        if soup is None:
            print(f"Couldn't load the Page: {url_profile}")
            return []

        # Now the extraction...
        css_profile = '.storyStream > div'  # Select the posts from a user profile
        css_page = '#recent > div > div > div'  # Select the posts from a Facebook page
        css_group = '#m_group_stories_container > div > div'  # Select the posts from a Facebook group
        raw_data = soup.select(f'{css_profile} , {css_page} , {css_group}')  # Now join and scrape it
        posts = []
        for item in raw_data:  # Now, for every post...
            published = item.select_one('abbr')  # Get the formatted datetime of published
            description = item.select('p')  # Get list of all p tag, they compose the description
            images = item.select('a > img')  # Get list of all images
            _external_links = item.select('p a')  # Get list of any link in the description, this are external links
            post_url = item.find('a', text=self.post_url_text)  # Get the url to point this post.
            like_url = item.find('a', text='Like')  # Get the Like url.

            # Clean the publish date
            if published is not None:
                published = published.get_text()
            else:
                published = ''

            # Join all the text in p tags, else set empty string
            if len(description) > 0:
                description = '\n'.join([d.get_text() for d in description])
            else:
                description = ''

            # Get all the images links
            images = [image.get('src', '') for image in images]

            # Clean the post link
            if post_url is not None:
                post_url = post_url.get('href', '')
                if len(post_url) > 0:
                    post_url = f'https://www.facebook.com{post_url}'
                    p_url = urlparse(post_url)
                    qs = parse_qs(p_url.query)
                    if not is_group:
                        post_url = f'{p_url.scheme}://{p_url.hostname}{p_url.path}?story_fbid={qs["story_fbid"][0]}&id={qs["id"][0]}'
                    else:
                        post_url = f'{p_url.scheme}://{p_url.hostname}{p_url.path}/permalink/{qs["id"][0]}/'
            else:
                post_url = ''

            # Clean the Like link
            if like_url is not None:
                like_url = like_url.get('href', '')
                if len(like_url) > 0:
                    like_url = f'https://m.facebook.com{like_url}'
            else:
                like_url = ''

            # Get list of external links in post description, if any inside
            external_links = []
            for link in _external_links:
                link = link.get('href', '')
                try:
                    a = link.index("u=") + 2
                    z = link.index("&h=")
                    link = unquote(link[a:z])
                    link = link.split("?fbclid=")[0]
                    external_links.append(link)
                except ValueError as e:
                    continue
            post = {'published': published, 'description': description, 'images': images,
                    'post_url': post_url, 'external_links': external_links, 'like_url': like_url}
            posts.append(post)
            self.posts.append(post)
        return posts

    def posts_to_csv(self, filename):
        if filename[:-4] != '.csv':
            filename = f'{filename}.csv'

        df = pd.DataFrame(self.posts)
        df.to_csv(filename)

    def posts_to_excel(self, filename):
        if filename[:-5] != '.xlsx':
            filename = f'{filename}.xlsx'

        df = pd.DataFrame(self.posts)
        df.to_excel(filename)

    def posts_to_json(self, filename):
        if filename[:-5] != '.json':
            filename = f'{filename}.json'

        with open(filename, 'w') as f:
            f.write('[')
            for entry in self.posts:
                json.dump(entry, f)
                f.write(',\n')
            f.write(']')
