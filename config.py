import os
abs_path = os.path.dirname(os.path.realpath(__file__))

bot_name = 'Akira'
log_file = '%s/logfile' % abs_path

tracking_code = '''
<!-- statcounter/analytics/whatever -->
'''

irc = {
  'nick': 'Akira',
  'servers': [
    {
      'connection': {
        'server': 'irc.akirabot.ml',
        'port': 6667,
        'username': None,
        'password': None,
      },
      'channels': [
        '#AkiraBotChat',
        '#AkiraBot',
        '#Akira'
      ]
    }
  ]
}

twitter = {
  'consumer_key': '',
  'consumer_secret': '',
  'access_token_key': '',
  'access_token_secret': '',
  'username': 'AkiraChatBot',
  'responses_log': 'twitter_responses'
}

facebook = {
  'page_id': ''
}

eventful = {
  'api_key': ''
}

lastfm = {
  'api_key' : ''
}

openweathermap = {
  'api_key': ''
}

wolfram = {
  'api_key': ''
}