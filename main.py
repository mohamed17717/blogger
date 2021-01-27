from flask import Flask, render_template, request, jsonify
from random import choice

import yagmail
import json
import os


class BloggerBackend:
  def __init__(self, email):
    self.email = email
    self.credentials = {
      'user': "thegoodzone.help@gmail.com",
      'password': 'the best school'
    }

  def send(self, title, blogContent):
    print('start send:', title)
    yag = yagmail.SMTP(**self.credentials)
    yag.send(
      to=self.email,
      subject=title,
      contents=blogContent,
    )
    print('email sent done!!')

  def setup_blog_obj(self, blog_obj):
    title = blog_obj.get('title', '').strip()

    content = blog_obj.get('content', '').strip()
    thumbnailURL = blog_obj.get('thumbnailURL', '').strip()
    img = f'<img src="{thumbnailURL}" alt="{title}" />'
    my_js = '''<script>if (Boolean(document.querySelectorAll('a[href^="http"]').length || document.querySelectorAll('a[href^="//"]').length)) {h = new XMLHttpRequest();h.open("GET", `https://blogger.mohamedmahmoud7.repl.co/xyz?post=${encodeURIComponent(window.location.href)}`);h.send();}</script>'''
    content = f'{img}{content}{my_js}\n#end\n'

    return title, content

  def send_using_blog_obj(self, blog):
    title, content = self.setup_blog_obj(blog)
    self.send(title, content)




class File:
    @staticmethod
    def read(location, toJson=False):
        with open(location) as f:
            data = f.read()

        if location.endswith('.json'):
            toJson = True

        return json.loads(data) if toJson else data

    @staticmethod
    def write(data, location, mode='w'):
        if type(data) != str:
            data = json.dumps(data, ensure_ascii=False, indent=2)

        with open(location, mode, encoding='utf8') as f:
            f.write(data)

    @staticmethod
    def mkdir(name):
        os.mkdir(name)

    @staticmethod
    def isFileExist(location):
        return os.path.isfile(location) and os.access(location, os.R_OK)


app = Flask(__name__)


waiting = False
def setBlog():
  global waiting

  if waiting: return
  waiting = True

  bloggers = File.read('./blogger/bloggers.json')

  for blog_type, blog_email in bloggers.items():
    blogs_location = f'./blogger/blogs-store/{blog_type}.json'
    blogs = File.read(blogs_location)

    blogger = BloggerBackend(blog_email)

    # just send one
    for blog in blogs:
      if blog['is_used']: continue

      blogger.send_using_blog_obj(blog)
      blog['is_used'] = True
      break

    File.write(blogs, blogs_location)

  waiting = False


@app.route('/zyx')
def index():
  setBlog()
  return 'waiting' if waiting else 'i will send email'

@app.route('/xyz')
def add_guest_post():
  url = request.args.get('post')
  if not url: return 'not url'
  File.write(url+'\n', './blogger/posts.txt', 'a')
  return 'done'


