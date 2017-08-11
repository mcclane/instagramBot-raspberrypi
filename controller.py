import requests
import time
from getpass import getpass
from random import randint

from bot import *

############
## CONSTANTS
############
delay = 60
howlong = 1000 #tags


####################
## get the resources
####################
c = open("resources/compliment_words.txt", "r")
h = open("resources/hashtags.txt", "r")
cl = c.readlines()
hl = h.readlines()
c.close()
h.close()
followed_file = open("resources/followed.txt", "a")

##########
##  URLs
##########
#TAG_URL = "https://www.instagram.com/explore/tags/%s/?__a=1&max_id=1"
TAG_URL = "https://www.instagram.com/explore/tags/%s"
PHOTO_BASE_URL = "https://www.instagram.com/p/%s"


##########################################
## Start controlling the bot
##########################################
b = bot(input("username: "), getpass())
b.follow("taylorswift")
b.unfollow("taylorswift")

##########################################
## Get initial following count
##########################################
#initial_following_count = b.get_following_count()
initial_following_count = 350


followed_list = []
for i in range(howlong):
    ##########################################
    ## Scrape user IDs, photo URLs from tag
    ##########################################
    tag = hl[randint(0,len(hl)-1)].strip()
    req = requests.get(TAG_URL % tag)
    photo_urls = [ PHOTO_BASE_URL % code for code in re.findall("\"code\": \"(\S+)\"", req.text) ]
    usernames = [ b.get_username(userid) for userid in re.findall("\"owner\": \{\"id\": \"(\d+)\"\}", req.text) ]
    ##########################################
    ## Like, maybe comment, follow, unfollow
    ##########################################
    for i in range(len(photo_urls)):
        b.like(photo_url=photo_urls[i])
        if(i == int(len(photo_urls)/2)):
            b.comment(message="You are so "+cl[randint(0, len(cl)-1)]+"!", photo_url=None)
        if(b.follow(usernames[i])):
            followed_file.write(usernames[i]+"\n")
            followed_list.append(usernames[i])
            if(len(followed_list) < 50): 
                time.sleep(delay)
                continue
            b.unfollow(followed_list[0]) 
            followed_list.pop(0)
        time.sleep(delay)

print("Non-unfollowed users: "+str(followed_list))
followed_file.close()

###########################
# Unfollow all the leaks
###########################
current_following_count = b.get_following_count()
#current_following_count = 394
leak = current_following_count - initial_following_count
print(current_following_count, initial_following_count, leak)
b.unfollow_n_most_recent(leak)
