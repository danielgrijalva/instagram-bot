# instagram-bot

## Installation
### Requirements
* Python 3.6+
* Firefox 68.0+
* Tested on Windows 10

### Installation

1. Create an isolated environment for the project with with `virtualenv`

    ```
    pip install virtualenv
    ```
2. Create a virtual environment inside the project
    ```
    virtualenv [name] 
    ```
    Hint: a common name to use is "venv"

3. Activate the environment  
  * On Windows:
    ```
    source venv/Scripts/activate
    ```
  * On Linux:
    ```
    source venv/bin/activate
    ```
    After activating, you will notice that **(venv)** appears before the command line.
  
 4. Install the required packages used in the project
 
     ```
     pip install -r requirements.txt
     ```
 
    Because we're using [InstaPy](https://github.com/timgrossmann/InstaPy/tree/master/instapy), it downloads everything needed to automate browser interactions, e.g. [Chrome Driver](https://chromedriver.chromium.org/) or [Gecko Driver](https://github.com/mozilla/geckodriver/releases) (Firefox).  
 
Now everything is installed and the project is ready to run.
 
### Account setup
Open the file `.env`, which looks like this:
```
ACCOUNT=
PASSWORD=
```
Fill in your credentials. This is the account that will log into Instagram to scrape the data.
 
### Running the script
In a terminal, run:
```
python run.py
```
The script then asks for input
```
Username? [account you want to analyze]
How many posts? [number of posts you want to analyze (up to 12 due Instagram limitations)]
```
  Note: you must activate the virtual environment first or else it will not load the necessary packages.

#### Process
1. First, the script will obtain the list of followers.
2. Then it will "sleep" a few seconds or minutes to avoid bans.
3. Obtain up to 24 latest posts, but just grab the amount you entered (up to 12).
4. Get list of likers for each post, taking breaks once in a while to avoid bans.
5. Now that we have all the required list of accounts, save them as CSV files.
    * It will create a folder for the account you entered (and use its username as name)
    * Inside that folder, you will see the following files:
      * `Followers.csv`: full list of followers
      * `Liked [post ID].csv`: list of accounts that liked post `post ID`
6. For each post, compare its list of likers against the followers list, pick every follower who liked the post and put them in a separate list (called `followers_who_liked`).
7. Count number of accounts in `followers_who_liked` to calculate the percentage of follower attachment.
8. Print to console the percentage for each post.
9. Print an average followers-likes ratio for the account.
10. Run through each follower and categorize them into `Liked 1+/2+/3+/0 posts` CSV files.
11. Close the browser process and finish :)

The whole process can take up to 2 and a half hours (for accounts with 5500+ followers, with small accounts it takes 10-30 minutes depending on the amount of posts scraped) if you analyze the maximum amount of posts (12). That's because the script sleeps/takes breaks often to avoid Instagram's rate limit and banning. This is a robust and safe approach, I runned the script several times for accounts with big/medium/small accounts and never got banned. Thank InstaPy for their awesome code!

### Troubleshooting
Sometimes the scraper refuses to log in due to a non-existing cookie or an extension error. What worked for me was deleting the `extension.xpi` file in the InstaPy home folder (located at `C:\Users\[user]\InstaPy\assets` or `~/InstaPy/assets`).  
