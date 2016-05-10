import requests, akira, re, custom_responses
from random import choice
from inspect import isclass

def make_response(text):
  for x in dir(custom_responses):
    _ = getattr(custom_responses, x)
    if not isclass(_):
      continue
    
    _cr = _()
    
    if not getattr(_cr, '__patterns__', None):
      continue
    
    if not callable(getattr(_cr, '__process__', None)):
      continue
    
    for pattern in _cr.__patterns__:
      regex = re.compile(pattern,
        re.MULTILINE | re.IGNORECASE | re.DOTALL)
      
      matches = regex.findall(text)
      if matches:
        query = matches[0]
        response = _cr.__process__(query)
        if response:
          return response
  
  try:
    response = akira.chatbot.get_response(text)
  except:
    response = choice('Maybe...', '...', '...right...')
  
  return response