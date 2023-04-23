# Adfly API

[![Downloads](https://pepy.tech/badge/adfly-api)](https://pepy.tech/project/adfly-api)
[![Downloads](https://pepy.tech/badge/adfly-api/month)](https://pepy.tech/project/adfly-api/month)
[![Downloads](https://pepy.tech/badge/adfly-api/week)](https://pepy.tech/project/adfly-api/week)

Unofficial Adfly API Python Wrapper

## &#x1F534; Status &#x1F534;
- Adf.ly joined [Linkvertise](https://linkvertise.com) as it was announced on their [Youtube Video](https://www.youtube.com/watch?v=EtjayoaWXg0)
- Linkvertise, unlike Adf.ly does not provide API endpoint instead has something called [Full Script API](https://blog.linkvertise.com/en/publisher/integrate-full-script-api/)
- Since Adf.ly is now down and no longer usable, this package and it's source code is invalid and archieved
- You are free fork or use this source code however you want.

## Obtaining API Credentials
To generate keys you should visit [here](https://adf.ly/publisher/tools#tools-api)

## Installation
`pip install adfly-api`

## Examples
```python
#Import
from adfly import AdflyApi

#Initialize
api = AdflyApi(
      user_id=12345678,
      public_key='xxxxxxxxxx',
      secret_key='xxxxxxxxxx',
)

# Url Groups examples.
api.get_groups()

# Expand examples.
api.expand(
    ['http://adf.ly/D', 'http://adf.ly/E', 'http://q.gs/4'],
    [3, '1A', '1C'])
api.expand(None, '1F')

# Shorten examples.
api.shorten([
  'http://docs.python.org/library/json.html',
  'https://github.com/benosteen'],
)
api.shorten('http://docs.python.org/library/json.html')

# Urls examples.
api.get_urls()
api.get_urls(search_str='htmlbook')
api.update_url(136, advert_type='int', group_id=None)
api.update_url(136, title='一些中国', fb_description='fb о+писан  и+е', fb_image='123')
api.delete_url(136)
```

## Credits
Originally developed by [Ben O'Steen](https://github.com/benosteen)
