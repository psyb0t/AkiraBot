import os, akira, cgi, re

from bs4 import BeautifulSoup
from datetime import datetime
from base64 import b64encode
from flask import Flask, request, render_template
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

debug = False
app = Flask(__name__)
app.jinja_env.cache = None

def txt2html(text):
  text = text.replace('\n', '<br>')
  
  return text

def post_handler(form):
  if not 'action' in form:
    return ''
  
  action = form['action']
  if action == 'chat':
    if 'user_text' in form:
      response_text = ''
      response_image = False
      
      user_text = request.form['user_text']
      rsp = akira.fn.make_response(user_text)
      if type(rsp) == tuple:
        response_text, img_src = rsp
        with open(img_src, 'r') as f:
          response_image = b64encode(f.read())
        
        os.remove(img_src)
      else:
        response_text = rsp
      
      return render_template('akirabot/response.html',
        response_image=response_image,
        response_text=txt2html(cgi.escape(response_text))
      )
    
    return render_template('akirabot/chat.html')
  elif action == 'functions':
    return render_template('akirabot/functions.html')
  else:
    return '', 500

@app.route('/', methods=['GET', 'POST'])
def index():
  if request.method == 'POST':
    return post_handler(request.form)
  
  soup = BeautifulSoup(render_template(
    'akirabot/index.html', config=akira.config
  ), 'html5lib')
  
  return soup.prettify()

def run():
  if debug:
    app.run(host='127.0.0.1', port=8888, debug=True)
    return
  
  http_server = HTTPServer(WSGIContainer(app))
  http_server.bind(8888, address='127.0.0.1')
  http_server.start(4)
  IOLoop.instance().start()