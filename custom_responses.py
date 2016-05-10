import requests, akira, re, os

from time import time
from random import choice
from urllib import quote_plus
from urlparse import urlparse
from subprocess import check_output

class who_is():
  __patterns__ = [
    r'^who(?:|.*?) (?:was|is|are|were) ([\w\d \-\(\)\[\],]+)(?:|\?)$'
  ]
  
  def __process__(self, __input__):
    r = requests.get(
      ('https://en.wikipedia.org/w/api.php?format=json&'
      'action=query&prop=extracts&exintro=&'
      'explaintext=&redirects&titles=%s') % quote_plus(__input__)
    )
    
    try:
      cont = r.json()
      qres = cont['query']
      
      return qres['pages'][qres['pages'].keys()[0]]['extract'].encode('utf-8')
    except:
      return choice(['I don\'t know!?', 'I have no idea!', 'No idea!'])

class web_sshot():
  __patterns__ = [
    r'^(?:browsershot|show me) (http(?:|s):\/\/(?:.*?))$'
  ]
  
  def __process__(self, __input__):
    p_url = urlparse(__input__)
    if not p_url.scheme or not p_url.netloc:
      return False
    
    cmd = [
      '/usr/bin/env',
      'xvfb-run',
      '-a',
      '/usr/bin/env',
      'cutycapt',
      '--url=%s' % __input__,
      '--auto-load-images=on',
      '--print-backgrounds=on',
      '--max-wait=10000'
      '--min-width=1366',
      '--min-height=768',
      '--delay=2000',
      '--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 ' \
      '(KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36',
      '--out=/tmp/web_sshot.png'
    ]
    
    check_output(cmd)
    
    if not os.path.isfile('/tmp/web_sshot.png'):
      return False
    
    return 'Here\'s your screenshot of %s' % __input__, '/tmp/web_sshot.png'

class give_events():
  __patterns__ = [
    r'what(?:(?:\'s| is) happening in| events are in) (.*?) ' \
    '(today|this week|next week)(?:|\?)$'
  ]
  
  def __process__(self, __input__):
    import eventful
    from datetime import datetime
    
    api = eventful.API(akira.config.eventful['api_key'])
    
    place = __input__[0]
    period = __input__[1]
    
    events = api.call('/events/search',
      l=quote_plus(place), sort_order='date',
      sort_direction='ascending', date=period.lower()
    )
    
    if not events or not 'events' in events or not events['events'] \
      or not 'event' in events['events']:
        return 'I couln\'t find any events in %s %s.' % (
          place.title(), period.lower()
        )
    
    event_list = []
    needed_keys = [
      'title', 'start_time', 'stop_time',
      'venue_name', 'venue_address', 'postal_code'
    ]
    
    if type(events['events']['event']) != list:
      events['events']['event'] = [events['events']['event']]
    
    for event in events['events']['event']:
      for __ in needed_keys:
        if not __ in event or not event[__]:
          event[__] = ''
          continue
        
        event[__] = event[__]
      
      if event['start_time']:
        event['start_time'] = datetime.strptime(
          event['start_time'], '%Y-%m-%d %H:%M:%S'
        ).strftime('%b %d, %H:%M')
      
      if event['stop_time']:
        event['stop_time'] = datetime.strptime(
          event['stop_time'], '%Y-%m-%d %H:%M:%S'
        ).strftime('%b %d, %H:%M')
      
      event_desc = '"{title}" which starts at {start_time}{when_ends}. ' \
        'The location for this event: {place_name} {place_loc}'.format(
          title = event['title'],
          start_time = event['start_time'],
          when_ends = ' and ends at %s' % event['stop_time'] if \
            event['stop_time'] else '',
          place_name = event['venue_name'],
          place_loc = '%s%s' % (
            'which is at %s' % event['venue_address'] if \
              event['venue_address'] else '',
            'postal code %s' % event['postal_code'] if \
              event['postal_code'] else ''
          )
        )
      
      event_list.append(event_desc.strip() + '.')
    
    header = 'There are {num_evs} events in {ev_place} {ev_per}.'.format(
      num_evs=events['total_items'],
      ev_place=place.title(),
      ev_per=period.lower()
    )
    
    if int(events['total_items']) > len(event_list):
      header = '%s Here is a list of 10 events happening soon:' % header
    
    response = '%s\n\n%s' % (header, '\n'.join(event_list))
    
    return response

class artist_top_tracks():
  __patterns__ = [
    r'^what are the best songs by (.*?)(?:|\?)$'
  ]
  
  def __process__(self, __input__):
    artist = __input__
    
    r = requests.get(
      ('http://ws.audioscrobbler.com/2.0/?method=artist.gettoptracks&'
      'artist=%s&api_key=%s&format=json') % (
        quote_plus(artist), akira.config.lastfm['api_key']
      )
    )
    
    resultlist = []
    try:
      cont = r.json()
      items = cont['toptracks']['track']
      
      for item in items:
        resultlist.append(item['name'].encode('utf-8'))
    except:
      pass
    
    if not resultlist:
      return choice(['I don\'t know!?', 'I have no idea!', 'No idea!'])
    
    return 'Here\'s the list of the best songs by %s:\n%s' % (
      artist.title(), '\n'.join(
        ['%s. %s' % (i+1,x) for i,x in enumerate(resultlist)]
      ).encode('utf-8')
    )

class artist_top_albums():
  __patterns__ = [
    r'^what are the best albums by (.*?)(?:|\?)$'
  ]
  
  def __process__(self, __input__):
    artist = __input__
    
    r = requests.get(
      ('http://ws.audioscrobbler.com/2.0/?method=artist.gettopalbums&'
      'artist=%s&api_key=%s&format=json') % (
        quote_plus(artist), akira.config.lastfm['api_key']
      )
    )
    
    resultlist = []
    try:
      cont = r.json()
      items = cont['topalbums']['album']
      
      for item in items:
        resultlist.append(item['name'].encode('utf-8'))
    except:
      pass
    
    if not resultlist:
      return choice(['I don\'t know!?', 'I have no idea!', 'No idea!'])
    
    return 'Here\'s the list of the best albums by %s:\n%s' % (
      artist.title(), '\n'.join(
        ['%s. %s' % (i+1,x) for i,x in enumerate(resultlist)]
      ).encode('utf-8')
    )

class similar_artists():
  __patterns__ = [
    r'^what artists sound like (.*?)(?:|\?)$'
  ]
  
  def __process__(self, __input__):
    artist = __input__
    
    r = requests.get(
      ('http://ws.audioscrobbler.com/2.0/?method=artist.getsimilar&'
      'artist=%s&api_key=%s&format=json') % (
        quote_plus(artist), akira.config.lastfm['api_key']
      )
    )
    
    resultlist = []
    try:
      cont = r.json()
      items = cont['similarartists']['artist']
      
      for item in items:
        resultlist.append(item['name'].encode('utf-8'))
    except:
      pass
    
    if not resultlist:
      return choice(['I don\'t know!?', 'I have no idea!', 'No idea!'])
    
    return 'Here\'s the list of artists similar to %s:\n%s' % (
      artist.title(), '\n'.join(resultlist).encode('utf-8')
    )

class now_weather():
  __patterns__ = [
    r'^(?:how|what)(?:\'s| is) the weather(?:| like) in ([\w\d ,;\'\-]+)(?:|\?)$'
  ]
  
  def __process__(self, __input__):
    location = __input__
    
    r = requests.get(
      ('http://api.openweathermap.org/data/2.5/weather?'
      'units=metric&q=%s&appid=%s') % (
        quote_plus(location), akira.config.openweathermap['api_key']
      )
    )
    
    response = ''
    try:
      cont = r.json()
      desc = cont['weather'][0]['description'].title()
      temp = cont['main']['temp']
      press = cont['main']['pressure']
      humid = cont['main']['humidity']
      wspeed = cont['wind']['speed']
      loc = '%s (%s)' % (cont['name'], cont['sys']['country'])
      
      response = 'The current weather conditions in {loc}:\n' \
      '{desc}\n' \
      u'Temperature: {temp}\u2103\n' \
      'Wind: {wspeed}m/s\n' \
      'Pressure: {press}hpa\n' \
      'Humidity: {humid}%'.format(
        loc=loc, desc=desc, temp=temp,
        wspeed=wspeed, press=press, humid=humid
      )
      
      return response
    except:
      return choice(['I don\'t know!?', 'I have no idea!', 'No idea!'])
    
class five_day_weather_forecast():
  __patterns__ = [
    r'^what(?:\'s| is) the weather forecast for ([\w\d ,;\'\-]+)(?:|\?)$'
  ]
  
  def __process__(self, __input__):
    from datetime import datetime
    
    location = __input__
    
    r = requests.get(
      ('http://api.openweathermap.org/data/2.5/forecast?'
      'units=metric&q=%s&appid=%s') % (
        quote_plus(location), akira.config.openweathermap['api_key']
      )
    )
    
    try:
      cont = r.json()
      loc = '%s (%s)' % (cont['city']['name'], cont['city']['country'])
      
      forecast = []
      for item in cont['list']:
        dt = datetime.strptime(
          item['dt_txt'], '%Y-%m-%d %H:%M:%S'
        ).strftime('On %b %d at %H:%M')
        desc = item['weather'][0]['description'].title()
        temp = item['main']['temp']
        press = item['main']['pressure']
        humid = item['main']['humidity']
        wspeed = item['wind']['speed']
        
        forecast.append(
          '{dt}:\n' \
          '{desc}\n' \
          u'Temperature: {temp}\u2103\n' \
          'Wind: {wspeed}m/s\n' \
          'Pressure: {press}hpa\n' \
          'Humidity: {humid}%'.format(
            dt=dt, desc=desc, temp=temp,
            wspeed=wspeed, press=press, humid=humid
          )
        )
      
      return 'The five day weather forecast for {loc}:\n' \
      '{forecast}'.format(
        loc=loc, forecast='\n\n'.join(forecast)
      )
    except:
      return choice(['I don\'t know!?', 'I have no idea!', 'No idea!'])

class random_cat_gif():
  __patterns__ = [
    r'^show me a (cat|kitty|kitten) gif(?:|!|\.)$'
  ]
  
  def __process__(self, __input__):
    a_what = __input__
    
    try:
      r = requests.get(
        'http://thecatapi.com/api/images/get?format=src&type=gif'
      )
      cont = r.content
    except:
      return False
    
    filename ='/tmp/cat_%s.gif' % str(time())
    
    with open(filename, 'w') as f:
      f.write(cont)
    
    return 'Here\'s a %s gif' % a_what, filename