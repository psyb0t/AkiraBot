import tweepy, os, akira
from datetime import datetime

auth = tweepy.OAuthHandler(
  akira.config.twitter['consumer_key'],
  akira.config.twitter['consumer_secret']
)

auth.set_access_token(
  akira.config.twitter['access_token_key'],
  akira.config.twitter['access_token_secret']
)

api = tweepy.API(auth, wait_on_rate_limit=True)

responses_file = '%s/%s' % (
  akira.config.abs_path, akira.config.twitter['responses_log']
)

def already_responded(_id, _type):
  if not os.path.isfile(responses_file):
    return False
  
  with open(responses_file, 'r') as f:
    for line in f:
      if '%s | %s' % (_type, _id) in line:
        return True
    
    return False
  
  return False

def add_response(_id, _type):
  with open(responses_file, 'a') as f:
    f.write('%s | %s\n' % (_type, _id))
  
  return

class mentions():
  @staticmethod
  def respond_latest(item_count=20):
    for mention in tweepy.Cursor(api.mentions_timeline).items(item_count):
      if already_responded(mention.id, 'mention'):
        continue
      
      tweet_text = mention.text.replace(
        '@%s' % akira.config.twitter['username'], ''
      ).strip()
      
      rsp = akira.fn.make_response(tweet_text)
      mention.text_no_at = tweet_text
      
      response = rsp
      image = None
      if type(rsp) == tuple:
        response, image = rsp
      
      mentions.respond(mention, response, image)
    
    return
  
  @staticmethod
  def respond(mention, send_text, image=False):
    akira.utils.log('Responding to mention by %s - %s:%s' % (
      mention.user.screen_name, mention.id, mention.text
    ))
    
    if image and not os.path.isfile(image):
      akira.utils.log('Inexistent file: %s' % image)
      return False
    
    if len(send_text) + len(mention.user.screen_name) > 138:
      akira.utils.log('Tweet length is over 140 characters.')
      send_text = 'I don\'t have a short answer for that. Sorry!'
    
    tweet = ('@%s %s') % (mention.user.screen_name, send_text)
    
    api.create_friendship(mention.user.id)
    
    try:
      if image:
        api.update_with_media(
          status='%s [%s]' % (tweet, str(datetime.now())),
          filename=image, in_reply_to_status_id=mention.id
        )
        
        os.remove(image)
      else:
        api.update_status(
          status=tweet, in_reply_to_status_id=mention.id
        )
    except:
      return False
    
    add_response(mention.id, 'mention')
    
    return True

class direct_messages():
  @staticmethod
  def respond_latest(item_count=20):
    for direct_message in tweepy.Cursor(
      api.direct_messages, full_text=True).items(item_count):
        if already_responded(direct_message.id, 'direct_message'):
          continue
        
        rsp = akira.fn.make_response(direct_message.text)
        
        response = rsp
        image = None
        if type(rsp) == tuple:
          response, image = rsp
        
        direct_messages.respond(direct_message, response, image)
  
  @staticmethod
  def respond(direct_message, send_text, image=False):
    akira.utils.log('Responding to direct message from %s - %s:%s' % (
      direct_message.sender.screen_name,
      direct_message.id, direct_message.text
    ))
    
    if image and not os.path.isfile(image):
      akira.utils.log('Inexistent file: %s' % image)
      return False
    
    api.create_friendship(direct_message.sender.id)
    
    try:
      if image:
        status = api.update_with_media(filename=image,
          status='@%s' % (direct_message.sender.screen_name)
        )
        
        status_url = status.extended_entities['media'][0]['url']
        send_text = '%s -> %s' % (send_text, status_url)
        
        os.remove(image)
      
      api.send_direct_message(
        user_id=direct_message.sender.id, text=send_text
      )
    except:
      return False
    
    add_response(direct_message.id, 'direct_message')
    
    return True

def run():
  if not api.verify_credentials():
    akira.utils.log('Invalid credentials')
  
  mentions.respond_latest(20)
  direct_messages.respond_latest(20)