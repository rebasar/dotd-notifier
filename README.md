# manning.com Deal of the Day Notifier

This is a simple script I hacked because I wasn't able to subscribe to
Manning's DotD mailing list (the captcha was loaded over HTTP instead
of HTTPS which caused a security exception in the browser). It is
designed to be run using cron or a similar command scheduler.

## Installation

Just clone the repository and run:

```sh
pip install -r requirements.txt
```

## Configuration

To run the script, you need a config file in your home directory named
`.dotd-notifier`. It is a simple config file in the Python
[ConfigParser](https://docs.python.org/2/library/configparser.html)
format. It consists of one optional and two mandatory sections.

```ini
[profile]
from_address: discount_bot@example.com
to_address: bookworm@example.com
# This can be either smtp or sendmail
mail_method: smtp

[books]
# This part is basically a set of
# key -> value pairs. The key is the
# last part of the URL for a given book
# For example:
# Go in Action: https://www.manning.com/books/go-in-action
# Becomes:
go-in-action: Go in Action
irresistible-apis: Irresistable APIs
re-engineering-legacy-software: Re-Engineering Legacy Software
# etc..

[smtp]
# This section is only required if
# you are using smtp as your mail
# method
server: mail.example.com:587
username: user.name
password: pass.word
tls: yes
```

## Usage

Just run `dotd-notifier` and if there are any matches to the books you
are following, you will receive an e-mail.

I recommend to setup a daily cron task for this purpose.

## TODO

- Decide on a error handling strategy. For now, we rely on cron
reporting errors.
- Customizable templates
- Change to proprietary license
- PROFIT!
