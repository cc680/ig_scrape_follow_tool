import os
import time
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager as CM
from getpass import getpass


# FOR TESTING ==================
#username = ''
#password = ''
# ==============================

ELEMENTS_TIMEOUT = 15
FOLLOW_DATA_LOADING_TIMEOUT = 50


def scrape(): 

    username = input('Username: ')
    password = getpass()



    options = webdriver.ChromeOptions()
    # TODO: invoking in headless removes need for GUI
    # options.add_argument("--headless")
    options.add_argument('--no-sandbox')
    options.add_argument("--log-level=3")

    mobile_emulation = {
        "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/535.19"}
    options.add_experimental_option("mobileEmulation", mobile_emulation)

    bot = webdriver.Chrome(executable_path=CM().install(), options=options)
    bot.set_window_size(600, 1000)

    bot.get('https://www.instagram.com/accounts/login/')

    time.sleep(2)

    print("Logging in...")

    user_element = WebDriverWait(bot, ELEMENTS_TIMEOUT).until(
        EC.presence_of_element_located((
            By.XPATH, '/html/body/div[1]/section/main/div/div/div[1]/div[2]/form/div/div[1]/div/label')))
            

    user_element.send_keys(username)

    pass_element = WebDriverWait(bot, ELEMENTS_TIMEOUT).until(
        EC.presence_of_element_located((
            By.XPATH, '/html/body/div[1]/section/main/div/div/div[1]/div[2]/form/div/div[2]/div/label')))

    pass_element.send_keys(password)

    login_button = WebDriverWait(bot, ELEMENTS_TIMEOUT).until(
        EC.presence_of_element_located((
            By.XPATH, '/html/body/div[1]/section/main/div/div/div[1]/div[2]/form/div/div[3]/button')))

    time.sleep(0.4)


    login_button.click()

    time.sleep(5)

    bot.get('https://www.instagram.com/{}/'.format(username))

    time.sleep(4.5)

    stats = bot.find_elements_by_class_name("_ac2a")
    num_followers = int(stats[1].text)
    num_following = int(stats[2].text)

    print('Followers: ' + str(num_followers))
    print('Following: ' + str(num_following))






    # getting followers
    if num_followers > 0:
        bot.get('https://www.instagram.com/{}/followers/'.format(username))

        time.sleep(3.5)

        ActionChains(bot).key_down(Keys.SHIFT).send_keys(Keys.TAB).key_up(Keys.SHIFT).perform()
        ActionChains(bot).key_down(Keys.SHIFT).send_keys(Keys.TAB).key_up(Keys.SHIFT).perform()

    print('Scraping followers...')

    followers = set()

    not_loading_count = 0
    prev = 0
    while len(followers) < num_followers:

        ActionChains(bot).send_keys(Keys.END).perform()

        time.sleep(0.3)

        more_followers = bot.find_elements_by_xpath(
        "//a[@class='qi72231t nu7423ey n3hqoq4p r86q59rh b3qcqh3k fq87ekyn bdao358l fsf7x5fv rse6dlih s5oniofx m8h3af8h l7ghb35v kjdc1dyq kmwttqpk srn514ro oxkhqvkx rl78xhln nch0832m cr00lzj9 rn8ck1ys s3jn8y49 icdlwmnq notranslate _a6hd']")
        
        followers.update(more_followers)

        #print(len(followers))
        if len(followers) == prev:
            not_loading_count += 1
        else:
            not_loading_count = 0
        if not_loading_count == FOLLOW_DATA_LOADING_TIMEOUT:
            break
        prev = len(followers)

    users_followers = set()
    c = 0
    for i in followers:
        if i.get_attribute('href'):
            c += 1
            follower = i.get_attribute('href').split("/")[3]
            print(i.get_attribute('href'))
            users_followers.add(follower)
            #print (c, ' ', follower)
        else:
            continue        

    print('Saving to file...')
    print('[DONE] - Your followers are saved in followers.txt file')

    with open('followers.txt', 'w') as file:
        file.write('\n'.join(users_followers) + "\n")









    # FOLLOWING

    if num_following > 0:
        bot.get('https://www.instagram.com/{}/following/'.format(username))
        time.sleep(3.5)

        ActionChains(bot).key_down(Keys.SHIFT).send_keys(Keys.TAB).key_up(Keys.SHIFT).perform()
        ActionChains(bot).key_down(Keys.SHIFT).send_keys(Keys.TAB).key_up(Keys.SHIFT).perform()

    print('Scraping following...')

    following = set()

    not_loading_count = 0
    prev = 0

    while len(following) < num_following:
        ActionChains(bot).send_keys(Keys.END).perform()

        time.sleep(.3)

        more_following = bot.find_elements_by_xpath(
        "//a[@class='qi72231t nu7423ey n3hqoq4p r86q59rh b3qcqh3k fq87ekyn bdao358l fsf7x5fv rse6dlih s5oniofx m8h3af8h l7ghb35v kjdc1dyq kmwttqpk srn514ro oxkhqvkx rl78xhln nch0832m cr00lzj9 rn8ck1ys s3jn8y49 icdlwmnq notranslate _a6hd']") 

        following.update(more_following)

        print(len(following))
        if len(following) == prev:
            not_loading_count += 1
        else:
            not_loading_count = 0
        if not_loading_count == FOLLOW_DATA_LOADING_TIMEOUT:
            break
        prev = len(following)

    # Getting url from href attribute
    c = 0
    users_following = set()
    for i in following:
        if i.get_attribute('href'):
            c += 1
            f = i.get_attribute('href').split("/")[3]
            print(i.get_attribute('href'))
            users_following.add(f)
            #print (c, ' ', f)
        else:
            continue            

    print('Saving...')
    print('[DONE] - Your following are saved in following.txt file')

    with open('following.txt', 'w') as file:
        file.write('\n'.join(users_following) + "\n")        

    not_follow_back = set()
    for f in users_following:
        if f not in users_followers:
            not_follow_back.add(f)
    
    print('[DONE] - Users that don\'t follow back are saved in non_followers.txt file')
    with open('non_followers.txt', 'w') as file:
        file.write('\n'.join(not_follow_back) + "\n")


    # Allowlist
    allow_list = set()
    a = None
    while True:
        a = input('Who do you want to place on the allow-list (allowed to not follow you)? Press enter to skip: ')
        if not a:
            break;
        if a not in not_follow_back:
            print('Error: ' + a + ' is not in the list of users that don\'t follow you back')
        else:
            allow_list.add(a)
    
    with open('allow_list.txt', 'w') as file:
        file.write('\n'.join(allow_list) + "\n")

    i = None
    i = input('Automatically unfollow unfollowers? (y/n): ').lower()    
    while i != 'y':
        if i == 'n':
            print('Exiting..')
            return
        i = input('Error: Please input y or n:').lower()


    unfollowed = set()
    # go to profiles, click unfollow button
    print('Unfollowing..')
    for f in not_follow_back:
        if f in allow_list:
            continue
        bot.get('https://www.instagram.com/{}/'.format(f))

        time.sleep(3)

        present = len(bot.find_elements_by_class_name('_acan _acap _acat')) > 0
        if present > 0:

            unfollow_button = WebDriverWait(bot, ELEMENTS_TIMEOUT).until(
                EC.presence_of_element_located((
                    By.XPATH, '/html/body/div[1]/div/div/div/div[1]/div/div/div/div[1]/section/main/div/header/section/div[1]/div[1]/div/div[2]/button')))
                            

            time.sleep(0.4)
            unfollow_button.click()

            unfollow_button = WebDriverWait(bot, ELEMENTS_TIMEOUT).until(
                EC.presence_of_element_located((
                    By.XPATH, '/html/body/div[1]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]/button[1]')))

            time.sleep(0.8)
            unfollow_button.click()
            unfollowed.add(f)


    print('Done unfollowing')
    print('Unfollowed the following users:')
    for u in unfollowed:
        print(u)
    print('Exiting...')

if __name__ == '__main__':
    scrape()
