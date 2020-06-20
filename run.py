import os
import csv
import random
import types
import pathlib
from time import sleep, time
from pprint import pprint
from dotenv import load_dotenv
from instapy.xpath import read_xpath
from instapy import InstaPy, smart_run, set_workspace
from instapy.util import highlight_print, click_element
from instapy.util import close_dialog_box, update_activity, get_users_from_dialog
from instapy.util import scroll_bottom, progress_tracker, web_address_navigator
from instapy.commenters_util import get_photo_urls_from_profile, check_exists_by_xpath
from selenium.common.exceptions import NoSuchElementException 


def get_likes_from_posts(self, username, photos_grab_amount, randomize=False, sleep_delay= 600):
        """ Get user's likers """
        if self.aborting:
            return self

        message = "Retrieving posts and their likers.."
        highlight_print(self.username, message, "feature", "info", self.logger)

        # to avoid banning, we only support up to 12 posts per session
        if photos_grab_amount > 12:
            self.logger.info(
                "Sorry, you can only grab likers from first 12 photos for "
                "given username now.\n"
            )
            photos_grab_amount = 12

        relax_point = random.randint(7, 14)  # you can use some plain value
        # `10` instead of this quitely randomized score
        self.quotient_breach = False

        # obtain post urls
        photo_urls = get_photo_urls_from_profile(
            self.browser, username, photos_grab_amount, randomize
        )
        sleep(1)
        # in case user only has 1 post, convert the returned value to a list
        if not isinstance(photo_urls, list):
            photo_urls = [photo_urls]

        # save post url and its likers
        data = {}
        for photo_url in photo_urls:
            if self.quotient_breach:
                break

            likers = users_liked(self.browser, photo_url)
            # This way of iterating will prevent sleep interference
            # between functions
            random.shuffle(likers)
            data[photo_url] = likers

        return data

def users_liked(browser, photo_url):
    photo_likers = []
    try:
        # go to the specified post
        web_address_navigator(browser, photo_url)
        # obtain list of accounts that liked the post
        photo_likers = likers_from_photo(browser)
        sleep(2)
    except NoSuchElementException:
        print("Could not get information from post: " + photo_url, " nothing to return")

    return photo_likers

def likers_from_photo(browser):
    """ Get the list of users from the 'Likes' dialog of a photo """

    try:
        # find the button that opens the "liked by" popup
        if check_exists_by_xpath(
            browser, read_xpath(likers_from_photo.__name__, "second_counter_button")
        ):
            liked_this = browser.find_elements_by_xpath(
                read_xpath(likers_from_photo.__name__, "second_counter_button")
            )
            element_to_click = liked_this[0]
        elif check_exists_by_xpath(
            browser, read_xpath(likers_from_photo.__name__, "liked_counter_button")
        ):

            liked_this = browser.find_elements_by_xpath(
                read_xpath(likers_from_photo.__name__, "liked_counter_button")
            )
            likers = []

            for liker in liked_this:
                if " like this" not in liker.text:
                    likers.append(liker.text)

            if " others" in liked_this[-1].text:
                element_to_click = liked_this[-1]

            elif " likes" in liked_this[0].text:
                element_to_click = liked_this[0]

            else:
                print(
                    "Few likes. Got photo likers: {}\n".format(likers)
                )
                return likers
        else:
            print("Couldn't find liked counter button. May be a video.")
            print("Moving on..")
            return []

        sleep(1)
        # get the amount of likes of the post
        max_likes = int(element_to_click.get_attribute('text').split()[0])
        click_element(browser, element_to_click)
        print("Opening likes...")
        # update server calls
        update_activity(browser, state=None)
        sleep(1)

        # get a reference to the liked by popup
        dialog = browser.find_element_by_xpath(
            read_xpath("class_selectors", "likes_dialog_body_xpath")
        )

        # scroll down the page
        previous_len = -1
        browser.execute_script(
            "arguments[0].scrollTop = arguments[0].scrollHeight", dialog
        )
        update_activity(browser, state=None)
        sleep(1)

        # start tracking time
        start_time = time()
        user_list = []

        while (
            not user_list
            or (len(user_list) != previous_len)
            and (len(user_list) < max_likes)
        ):

            # check if we scrolled through the whole lsit
            if previous_len + 10 >= max_likes:
                print('\nScrolling finished')
                if max_likes < 10:
                    user_list = get_users_from_dialog(user_list, dialog)
                sleep(1)
                break

            previous_len = len(user_list)
            scroll_bottom(browser, dialog, 2)

            # retrieve list from liked by popup
            user_list = get_users_from_dialog(user_list, dialog)

            # write & update records at Progress Tracker
            progress_tracker(len(user_list), max_likes, start_time, None)

        print('\n')
        random.shuffle(user_list)
        sleep(1)

        # close liked by popup
        close_dialog_box(browser)
        print(
            'Got {} likers'.format(len(user_list))
        )
        return user_list

    except Exception as exc:
        print('Some problem occured!\n\t{}'.format(str(exc).encode('utf-8')))
        return []

def load_credentials():
    """ Loads your account and password from .env file """
    load_dotenv(override=True)
    username = os.getenv('ACCOUNT')
    password = os.getenv('PASSWORD')

    return username, password

def write_csv(username, filename, data):
    # create folder
    pathlib.Path(username).mkdir(exist_ok=True)
    # folder name + file name
    filepath = f'{username}/{filename}.csv'
    # write CSV data
    with open(filepath, 'w', newline='') as file:
        wr = csv.writer(file, delimiter="\n")
        wr.writerow(data)

if __name__ == '__main__':
    # set workspace folder at desired location (default is at your home folder)
    set_workspace(path=None)
    # get an InstaPy session
    username, password = load_credentials()
    # to see the browser and the bot in real time, set `headless_browser` to False
    session = InstaPy(username=username, password=password, headless_browser=True)

    with smart_run(session):
        username = input('> Username? ')
        photo_amount = int(input('> How many posts? ' ))

        # add custom method to InstaPy object
        session.__dict__['get_likes_from_posts'] = types.MethodType(get_likes_from_posts, session)
        
        # grab followers and save as CSV
        followers = session.grab_followers(username=username, amount='full', live_match=True, store_locally=False)
        write_csv(username, 'Followers', followers)

        # grab likers from X latest posts and save them as CSV
        posts = session.get_likes_from_posts(username=username, photos_grab_amount=photo_amount)    
        percentages = []
        for post, likers in posts.items():
            post_id = post.split('/')[-2]
            filename = f'Liked {post_id}'
            # write post data to CSV file
            write_csv(username, filename, likers)

            # calculate attachment ratio
            followers_who_liked = (account in followers for account in likers)
            percent = (sum(followers_who_liked) * 100) / len(followers)
            percentages.append(percent)
            print(f'Attatchment ratio for post {post_id}: {percent:.2f}%')

        # categorize followers by how many posts they liked
        follower_by_likes = {0: [], 1: [], 2: [], 3: []}
        for follower in followers:
            liked = 0
            for _, likers in posts.items():
                if follower in likers:
                    liked += 1
                if liked >= 3:
                    break
            
            follower_by_likes[liked].append(follower)

        # write each liked categories to CSV
        for likes, followers in follower_by_likes.items():
            filename = f'Liked {likes}'
            write_csv(username, filename, followers)


        # average follower-likes ratio for the account
        average_ratio = sum(percentages) / len(percentages)
        print(f'Average follower-like ratio for {username}: {average_ratio:.2f}%')
