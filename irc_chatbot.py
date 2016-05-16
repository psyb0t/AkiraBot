import akira, irc.client, sys, os

nick = akira.config.irc['nick']

def _log(msg):
  akira.utils.log('[IRC] %s' % msg)

def on_connect(conn, event, channels=[]):
  _log('Connected to %s' % event.source)
  for channel in channels:
    conn.join(channel)

def on_join(conn, event):
  srcuname = nick_from_source(event.source)
  who = srcuname
  if srcuname == nick:
    who = 'I'
  else:
    send_message(
      conn, srcuname, 'Welcome! Would you like me to fire the "laser"?'
    )
  
  _log('%s joined %s' % (who, event.target))

def on_disconnect(conn, event):
  _log('Disconnected...')

def on_msg(conn, event):
  nick = nick_from_source(event.source)
  msg = event.arguments[0].replace(
    '%s:' % nick, ''
  ).strip()
  
  if event.type == 'pubmsg':
    target = event.target
  elif event.type == 'privmsg':
    target = nick
  
  _log('%s message seen - Source: @%s Message: %s' % (
    event.type.upper(), nick, msg
  ))
  
  if msg and target:
    response = akira.fn.make_response(msg)
    
    if type(response) == tuple:
      response = 'I will not send images in IRC!'
    
    response = response.replace('\n', ' \ ')
    if sys.getsizeof(response) > 512:
      response = 'My answer is larger than 512 bytes. ' \
        'IRC does not allow that, sorry!'
    
    if event.type == 'pubmsg':
      response = '%s: %s' % (nick, response)
    
    send_message(conn, target, response)
    

def send_message(conn, target, msg):
  conn.privmsg(target, msg)
  _log('Sent message - Target: %s Message: %s' % (
    target, msg
  ))

def nick_from_source(source):
  return source.split('!~')[0]

def run():
  children = []
  for server in akira.config.irc['servers']:
    server['connection']['nickname'] = nick
    pid = os.fork()
    if not pid:
      reactor = irc.client.Reactor()
      c = reactor.server().connect(
        **server['connection']
      )
      
      def _on_connect(conn, event):
        return on_connect(
          conn, event, server['channels']
        )
      
      c.add_global_handler('welcome', _on_connect)
      c.add_global_handler('join', on_join)
      c.add_global_handler('disconnect', on_disconnect)
      
      c.add_global_handler('privmsg', on_msg)
      c.add_global_handler('pubmsg', on_msg)
      
      reactor.process_forever()
      os._exit()
    else:
      children.append(pid)
  
  for child in children:
    os.waitpid(child, 0)