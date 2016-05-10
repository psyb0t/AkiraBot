import config
from datetime import datetime

def log(message):
  log_msg = '[%s] %s' % (str(datetime.now()), message)
  print log_msg
  with open(config.log_file, 'a') as f:
    f.write('%s\n' % log_msg)
  
  return