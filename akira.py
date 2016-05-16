#!/usr/bin/env python
import config, utils, os, fn, sys
# UTF-8 issue hack
reload(sys)
sys.setdefaultencoding("utf-8")

from chatterbot import ChatBot

chatbot = ChatBot(
  config.bot_name,
  logic_adapters=[
    'chatterbot.adapters.logic.EvaluateMathematically',
    'chatterbot.adapters.logic.TimeLogicAdapter',
    'chatterbot.adapters.logic.ClosestMatchAdapter'
  ],
  io_adapter='chatterbot.adapters.io.NoOutputAdapter',
  storage_adapter='chatterbot.adapters.storage.MongoDatabaseAdapter',
  database='akiradb', read_only=False
)

def train(_file=None):
  if _file:
    if not os.path.isfile(_file):
      sys.exit('Inexistent training file %s' % _file)
    
    with open(_file, 'r') as f:
      chatbot.train([
        x.strip() for x in f.readlines()
      ])
    
    return
  
  chatbot.train('chatterbot.corpus.english')
  
  return

if __name__ == '__main__':
  supported_methods = [
    'train', 'terminal', 'twitter', 'web', 'irc'
  ]
  args = sys.argv[1:]
  if not args:
    sys.exit('USAGE: %s [method]' % __file__)
  
  method = args[0]
  if method not in supported_methods:
    sys.exit('Unsupported method!')
  
  if method == 'train':
    _file = None
    if len(args) > 1:
      _file = args[1]
    
    train(_file)
    sys.exit()
  
  if method == 'terminal':
    try:
      while True:
        sys.stdout.write('You: ')
        user_input = str(raw_input())
        
        response = fn.make_response(
          user_input.encode('utf-8').strip()
        )
        
        img = ''
        if type(response) == tuple:
          response, img = response
        
        print '%s: %s' % (
          config.bot_name, '%s%s' %
          (response.encode('utf-8'), ': %s' % img if img else '')
        )
    except KeyboardInterrupt:
      sys.exit()
  
  module = __import__('%s_chatbot' % method)
  
  if method == 'web':
    if len(args) > 1:
      if args[1].strip() == 'debug':
        module.debug = True
  
  module.run()