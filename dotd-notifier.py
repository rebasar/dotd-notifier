#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys, os, requests, ConfigParser, smtplib
from email.mime.text import MIMEText
from subprocess import Popen, PIPE
from bs4 import BeautifulSoup

DOTD_URL = 'http://www.manning.com/dotd'
BOOK_URL_TEMPLATE = 'http://www.manning.com/books/%s'

class Book:
    def __init__(self, title, id):
        self.title = title
        self.id = id

    def __str__(self):
        return self.title.encode('utf-8')

    def __unicode__(self):
        return self.title

    def __repr__(self):
        return self.id.__repr__()

class SMTPConfig:
    def __init__(self, server, username=None, password=None, tls=False):
        self.server = server
        self.username = username
        self.password = password
        self.tls = tls
    
class UserProfile:
    def __init__(self, books, from_address, to_address, mail_method, smtp_config=None):
        self.books = books
        self.from_address = from_address
        self.to_address = to_address
        self.mail_method = mail_method
        self.smtp = smtp_config
    
def download_dotd():
    response = requests.get(DOTD_URL)
    assert response.status_code == 200
    return response.text

def process(html):
    parser = BeautifulSoup(html, 'html.parser')
    books = set([a.get('href').split('/')[-1] for a in parser.find_all('a') if a.get('href').startswith('/books')])
    code = parser.select("span#code")[0].string
    return code, books

def get_link(id):
    return BOOK_URL_TEMPLATE%id

def render_template(code, found):
    template = """Some items that you follow on manning.com has discounts!

{items}

Make sure you use the promo code: {code} during checkout.

Enjoy!
    """
    items = '\n'.join(['- %s (%s)'%(book.title, get_link(book.id)) for book in found])
    return template.format(code=code, items=items)

def assemble_mail(profile, code, found):
    body = render_template(code, found)
    msg = MIMEText(body, _charset="utf-8")
    msg['Subject'] = 'Books in discount on manning.com!'
    msg['To'] = profile.to_address
    msg['From'] = profile.from_address
    return msg

def send_notification_via_smtp(profile, message):
    smtp = smtplib.SMTP(profile.smtp.server)
    if profile.smtp.tls:
        smtp.starttls()
    if profile.smtp.username and profile.smtp.password:
        smtp.login(profile.smtp.username, profile.smtp.password)
    smtp.sendmail(profile.from_address, profile.to_address, message.as_string())
    smtp.quit()

def send_notification_via_sendmail(profile, message):
    p = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
    p.communicate(message.as_string())

def send_notification(profile, code, found):
    message = assemble_mail(profile, code, found)
    if profile.mail_method == "smtp":
        send_notification_via_smtp(profile, message)
    elif profile.mail_method == "sendmail":
        send_notification_via_sendmail(profile, message)
    else:
        raise Exception("Unknown notification mechanism: %s"%profile.mail_method)

def load_smtp_settings(config):
    try:
        server = config.get('smtp', 'server')
        username = config.get('smtp','username')
        password = config.get('smtp', 'password')
        tls = config.getboolean('smtp','tls')
        return SMTPConfig(server, username, password, tls)
    except:
        return None
    
def get_user_profile():
    config = ConfigParser.ConfigParser()
    config.read(os.path.expanduser('~/.dotd-notifier'))
    books = [Book(value, key) for key, value in config.items('books')]
    from_address = config.get('profile', 'from_address')
    to_address = config.get('profile', 'to_address')
    mail_method = config.get('profile', 'mail_method')
    smtp_config = load_smtp_settings(config)
    return UserProfile(books, from_address, to_address, mail_method, smtp_config)

def notify(code, results):
    profile = get_user_profile()
    found = [b for b in profile.books if b.id in results]
    if found:
        send_notification(profile, code, found)

def main():
    notify(*process(download_dotd()))
    return 0

if __name__ == '__main__':
    sys.exit(main())
