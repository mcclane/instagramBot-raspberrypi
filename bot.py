import time
import selenium
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import requests
import re

#my files
from logger import *

class bot(object):

    FOLLOW_URL = "https://www.instagram.com/web/friendships/%s/follow/"

    #set user agent to mobile, more importantly not phantomjs
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (iPhone; CPU iPhone OS 10_0 like Mac OS X) AppleWebKit/602.1.38 (KHTML, like Gecko) Version/10.0 Mobile/14A5297c Safari/602.1")
    driver = webdriver.PhantomJS(desired_capabilities=dcap)
    session = requests.Session()
    #users I don't want to unfollow
    w = open("resources/whitelist.txt", "r")
    wl = w.readlines()
    w.close()

    def __init__(self, username, password):
        self.username = username
        ####################################
        ## SET UP LOGGER
        ####################################
        self.l = logger(self.username+".log")

        ####################################
        ## LOGIN
        ####################################
        self.driver.get("https://www.instagram.com/accounts/login/")
        login_box = self.driver.find_element_by_name("username")
        login_box.send_keys(self.username)
        password_box = self.driver.find_element_by_name("password")
        password_box.send_keys(password)
        password_box.send_keys(Keys.ENTER)
        self.l.log("Logged in to "+username, "INFO")
        time.sleep(2)

        ####################################
        ## SETUP THE REQUESTS SESSION
        ####################################
        cookies = { cookie['name'] : cookie['value'] for cookie in self.driver.get_cookies() }
        requests.utils.add_dict_to_cookiejar(self.session.cookies, cookies)

    def follow(self, user):
        self.driver.get("https://www.instagram.com/"+user)
        time.sleep(1)
        while(True):
            try:
                follow_button = self.driver.find_element(By.XPATH, '//button[text()="Follow"]')
                follow_button.click()
                self.l.log("Followed user: "+user, "INFO")
                return True
                break
            except selenium.common.exceptions.StaleElementReferenceException:
                pass #needs to load
            except selenium.common.exceptions.NoSuchElementException:
                self.l.log("Can't find follow button for user: %s" % (user), "ERROR")
                return False
            except Exception as err:
                self.l.log("%s Trying follow user: %s" % (str(err), user), "ERROR")
                return False

    def unfollow(self, user):
        self.driver.get("https://www.instagram.com/"+user)
        time.sleep(1)
        while(True):
            try:
                unfollow_button = self.driver.find_element(By.XPATH, '//button[text()="Following"]')
                unfollow_button.click()
                self.l.log("Unfollowed user: "+user, "INFO")
                time.sleep(1)
                return True
                break
            except selenium.common.exceptions.StaleElementReferenceException:
                pass #needs to load
            except selenium.common.exceptions.NoSuchElementException:
                self.l.log("Can't find unfollow button for user: %s" % (user), "ERROR")
                return False
            except Exception as err:
                self.l.log("%s Trying unfollow user: %s" % (str(err), user), "ERROR")
                return False

    def like(self, photo_url=None):
        if(photo_url is not None):
            self.driver.get(photo_url)
        while(True):
            try:
                like_button = self.driver.find_element_by_class_name("coreSpriteHeartOpen")
                like_button.click()
                self.l.log("liked photo "+photo_url, "INFO")
                break
            except selenium.common.exceptions.StaleElementReferenceException:
                pass #needs to load
            except selenium.common.exceptions.NoSuchElementException:
                self.l.log("Can't find like button for photo : "+self.driver.current_url, "ERROR")
                break
            except Exception as err:
                self.l.log("%s Trying like photo: %s" % (str(err), self.driver.current_url), "ERROR")
                break

    def comment(self, message, photo_url=None):
        if(photo_url is not None):
            self.driver.get(photo_url)
        try:
            comment_sprite = self.driver.find_element_by_class_name("coreSpriteComment")
            comment_sprite.click()
            time.sleep(1)
            text_box = self.driver.find_element_by_class_name("_bilrf")
            time.sleep(1)
            text_box.send_keys(message)
            #text_box.send_keys(Keys.ENTER)
            post_button = self.driver.find_element_by_class_name("_55p7a")
            post_button.click()
            self.l.log("commented "+message+" on "+self.driver.current_url, "INFO")
        except Exception as err:
            self.l.log("%s Trying to comment on photo: %s" % (str(err), self.driver.current_url), "ERROR")

    def get_username(self, user_id):
        req = self.session.get(self.FOLLOW_URL % (user_id))
        #req = requests.get(self.FOLLOW_URL % (user_id), cookies=cookies)
        try:
            return re.search("username=(\S+)\"", req.text).group(1)
        except Exception as err:
            self.l.log("Error trying to convert ID: "+user_id+" to username..."+str(err), "ERROR")
            return "taylorswift"
    
    def get_following_count(self):
        self.driver.get("https://www.instagram.com/"+self.username)
        time.sleep(2)
        try:
            return int(self.driver.find_elements_by_class_name("_fd86t")[2].text.replace(",",""))
        except Exception as err:
            self.l.log("Error: %s \t while getting following count for self" % (str(err)), "ERROR")
            return 0


    def unfollow_n_most_recent(self, n):
        unfollow_count = 0
        while(True):
            if(unfollow_count >= n):
                break
            self.driver.get("https://www.instagram.com/"+self.username)
            time.sleep(2)
            follow_page_link = self.driver.find_element_by_xpath("//*[contains(text(), 'following')]")
            follow_page_link.click()
            time.sleep(2)
            unfollow_buttons = self.driver.find_elements_by_class_name("_qv64e")
            usernames = self.driver.find_elements_by_class_name("_2g7d5")
            for i in range(len(unfollow_buttons)):
                if(unfollow_count >= n):
                    break
                if(usernames[i].text in self.wl):
                    continue
                unfollow_buttons[i].send_keys(Keys.ENTER)
                unfollow_count += 1
                self.l.log("Unfollowed user: "+usernames[i].text, "INFO")
                time.sleep(30)
                self.driver.execute_script("window.scrollTo(0, "+str(52*unfollow_count)+");")
                time.sleep(1)
