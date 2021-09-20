#!/usr/bin/env python

import logging
import os
import modifydb
import requests
import random
import datetime

#pro part
from pr0gramm import *
import time


from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, CallbackQueryHandler, PicklePersistence

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

bot_persistence = PicklePersistence(filename='persistence_file')

logger = logging.getLogger(__name__)

#get api key from os environment
bot_api_key = os.environ.get("TG_BOT_KEY_PROWOZG")

#requesting and then excluding posts by tags
def update_bad_tags(context: CallbackContext) -> None:
    md = modifydb.Modifydb('/pr0/database/main.db')
    ignored_tags = ('text', 'Nie+mehr+CDU', 'pol', 'logo+nicht+verkackt', 'Deutsch', 'Baerbock')

    print('Updating ignored tags...')
    for tag in ignored_tags:
        request_string = 'https://pr0gramm.com/api/items/get?tags={}'.format(tag)
        response = requests.get(request_string)
        data = response.json()
        ajson = data

        for item in ajson['items']:
            item_id = item['id']
            item_url = item['image']
            item_sent = 'yes'
            md.insert_data(item_id, item_url, item_sent, full=None)
    
   
    #print('Done')
    return 

def get_good_posts(context: CallbackContext) -> None:
    md = modifydb.Modifydb('/pr0/database/main.db')
    good_tags = ('anime', 'kadse')

    for tag in good_tags:
        request_string = 'https://pr0gramm.com/api/items/get?tags={}'.format(tag)
        #logging.info('Trying: ' + request_string)
        response = requests.get(request_string)
        data = response.json()
        ajson = data

        for item in ajson['items']:
            item_id = item['id']
            item_url = item['image']
            item_sent = 'no'
            item_up = item['up']
            item_down = item['down']
            item_score = item_up - item_down
            #logging.info('Got: ' + str(item_id) + 'with score: ' + str(item_score))
            if (item_score > 50):
                md.insert_data(item_id, item_url, item_sent, full=None)
   
    #print('Done')
    return 


def get_top_posts(context: CallbackContext) -> None:

    md = modifydb.Modifydb('/pr0/database/main.db')
    
    print('Getting top posts...')
    api = Api() 

    time_days = 2

    top_posts = Posts()
    max_date = None
    for posts in api.get_items_iterator(promoted=1):
        top_posts.extend(posts)

        if max_date is None:
            max_date = top_posts.maxDate()

        if max_date - top_posts.minDate() >= 86400*time_days:
            break

        time.sleep(0.1)

    posts = top_posts
    top_posts = Posts()
    for post in posts:
        if post["created"] > max_date - 86400*time_days:
            top_posts.append(post)

    print('Saving top posts to DB...')
    for post in top_posts:
        top_id = post['id']
        top_url = post['image']
        top_audio = post['audio']
        top_height = post['height']
        top_width = post['width']

        logging.info('Looking at ' + str(top_id) + ' it has ' + str(top_audio) + ' and width and height are ' + str(top_height) + ' x ' + str(top_width) )

        #not adding if audio is True
        if top_audio:
            logging.info('Triggered audio = true on ' + str(top_id))
            continue
        
        #longposts are not welcome
        elif (((top_width + top_height // 2) // top_width) > 3):
            logging.info('triggered longpost on ' + str(top_id))
            continue
       
        else:    
            md.insert_data(top_id, top_url, 'no', '')

#trying to lessen the bad tags slipping in
def update_everything(context: CallbackContext) -> None:
    update_bad_tags(None)
    get_top_posts(None)
    get_good_posts(None)
    logging.info('Everything updated')

def send_post(context: CallbackContext) -> None:
    md = modifydb.Modifydb('/pr0/database/main.db')
    print('Selecting a post to send...')
    unsent = md.select_unsent()

    if unsent is None:
        print('Nothing to post from DB...')
        return None

    unsent_id = unsent[0]
    unsent_url = unsent[1]

    #print(unsent_id)
    #print(unsent_url)
    
    vid_url = 'https://vid.pr0gramm.com/'
    pic_url = 'https://img.pr0gramm.com/'
    
    try:
        if unsent_url.endswith(".jpg" or ".png"):
            full_unsent_url = pic_url + unsent_url
            logging.info('Sending: ' + str(unsent_id) + 'with url: ' + full_unsent_url)
            context.bot.sendPhoto(chat_id='@repost_this', photo=full_unsent_url, timeout=20)
        elif unsent_url.endswith(".mp4"):
            full_unsent_url = vid_url + unsent_url
            logging.info('Sending: ' + str(unsent_id) + ' with url: ' + full_unsent_url)
            context.bot.sendVideo(chat_id='@repost_this', video=full_unsent_url, timeout=40)
        else:
            print('Something is wrong with ' + unsent_url)
    except:
        logging.info('ERRORED OUT WHILE TRYING TO SEND ' + str(unsent_id) + 'with url: ' + full_unsent_url) 

    
    md.set_sent(unsent_id)

    # would be weird if it works
    random_sleep = random.randint(1,300)
    logging.info('Sleeping for ' + str(random_sleep))
    time.sleep(random_sleep)
    
    
    #random_seconds = datetime.datetime.now().replace(minute=random.randint(0,59))
    #context.job_queue.run_once(send_post, when=random_seconds)
    
    return 


def start(update: Update, context: CallbackContext) -> None:
    """start working when command /start is issued."""


    return
      



def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(bot_api_key, use_context=True,  persistence=bot_persistence)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    #job queue
    job_queue = updater.job_queue

    #job_gtp = job_queue.run_repeating(get_top_posts, interval=600, first=5)
    #job_sp = job_queue.run_repeating(send_post, interval=random.randrange(1200), first=15)
       
      
    #random_seconds = lambda: random.randint(30,1200)

    #job_queue.run_repeating(update_bad_tags, interval=120, first=5)
    #job_queue.run_repeating(get_top_posts, interval=180, first=10)
    #job_queue.run_repeating(get_good_posts, interval=360, first=15)
    job_queue.run_repeating(update_everything, interval=120, first=5)
    job_queue.run_repeating(send_post, interval=60, first=30)
    #job_queue.run_once(send_post, when=69)


    #job_queue.start()

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler('start', start, filters=Filters.user(username={'@agathakazar','@shift_touko'})))
    #dispatcher.add_handler(CommandHandler("help", help_command))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()