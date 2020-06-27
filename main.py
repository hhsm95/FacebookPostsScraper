from FacebookPostsScraper import FacebookPostsScraper as Fps
from pprint import pprint as pp


def main():
    # Enter your Facebook email and password
    email = 'YOUR_EMAIL'
    password = 'YOUR_PASSWORD'

    # Instantiate an object
    fps = Fps(email, password, post_url_text='Full Story')

    # Example with single profile
    single_profile = 'https://www.facebook.com/BillGates'
    data = fps.get_posts_from_profile(single_profile)
    pp(data)

    # Example with multiple profiles
    profiles = [
        'https://www.facebook.com/zuck',  # User profile
        'https://www.facebook.com/thepracticaldev',  # Facebook page
        'https://www.facebook.com/groups/python'  # Facebook group

    ]
    data = fps.get_posts_from_list(profiles)
    pp(data)

    fps.posts_to_csv('my_posts')  # You can export the posts as CSV document
    # fps.posts_to_excel('my_posts')  # You can export the posts as Excel document
    # fps.posts_to_json('my_posts')  # You can export the posts as JSON document


if __name__ == '__main__':
    main()
