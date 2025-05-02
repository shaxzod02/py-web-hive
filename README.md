# PyWebhive: Python Web Framework built for learning purposes

![purposes](https://img.shields.io/badge/purposes-learning-yellow)
![PyPI - Version](https://img.shields.io/pypi/v/pywebhive)


PyWebhive is a Python web framework built for learning purposes

It's a WSGI framework and can be used with any WSGI application server such as Gunicorn.

## Installation

```shell
pip install pywebhive
```

## How to use it 

### Basic Usage:

    
```Python
from pywebhive.api import PyWebHiveApp

    
app = PyWebHiveApp()


# Simple text response handlers
@app.route("/home", allowed_methods=["get"])
def home(request, response):
    response.text = "Hello from the Home Page"


# Parametrized handlers
@app.route("/hello/{name}")
def greeting(request, response, name):
    response.text = f"Hello {name}"


# Class-based handlers
@app.route("/books")
class Books:
    def get(self, request, response):
        response.text = "Books page"
    
    def post(self, request, response):
        response.text = "Endpoint to create a book\n"


# Explicit addition of handlers
def new_handler(request, response):
    response.text = "From new handler"

app.add_route("/new-handler", new_handler)


# Templates support
@app.route("/template")
def template(req, resp):
    resp.body = app.template(
        "home.html",
        context = {"new_title": "Best Title", "new_body": "Best Body"}).encode()
        


# JSON response handlers
@app.route("/json")
def json_handler(request, response):
    response_data = {"name": "some name", "type": "json"}
    response.json = response_data
```    

    




### Unit Tests
The recommended way of writing unit tests is with [pytest](https://docs.pytest.org/en/latest/).
There are two built in fixtures 
that you may want to use when writing unit tests with PyWebhive. The first one is "app" which is
an instance of the main 'API' class.

```Python
def test_basic_route_adding(app):
    @app.route('/home')
    def home(req, resp):
        resp.text = "Hello from Home"


def test_parametrized_routes(app, test_client):
    @app.route("/hello/{name}")
    def greeting(request, response, name):
        response.text = f"Hello {name}"

    assert test_client.get("http://testserver/hello/Sam").text == "Hello Sam"


def test_class_based_get(app, test_client):
    @app.route("/books")
    class Books:
        def get(self, request, response):
            response.text = "Books page"

    response = test_client.get("http://testserver/books")
    assert response.text == "Books page"
    assert response.status_code == 200  


### How we can use Templates?
### Using Templates
### We have to make dir name called temps
    @app.route("/temp")
    def template_handler(req, resp):
        resp.html = app.template(
            "home.html",
            context = {"new_title": "New title", "new_body": "New body"}
        )
```        

## Static Files
   
   Just like templates, the default folder for static files is 'static' and you can
   override it:

   ```Python
   app = API(static_dir="static_dir_name")
   ```

   Then you can use the files lnside this folder in HTML files:

   ```html
   <!DOCTYPE html>
   <html lang="en">

    <html>
    <header>
        <meta charset="UTF-8">
        <title>{{new_title}}</title>

        <link href="/static/home.css" rel="stylesheet" href="/static/home.css">
    </header>

    <body>
        {{new_body}}
    </body>
</html>
```

### Middleware

You can dreate custom middleware classes by inheriting from the °bumbo.middleware.
Middleware class and overriding its two methods that are called before and after each request:

```Python

from bumbo.api import API
from bumbo.middleware import Middleware

app = API()

class SimpleCustomMiddleware(Middleware):
    def __init__(self, app):
        self.app = app

    def process_request(self, req):
        print(f"Request: {req.url}")

    def process_response(self, req, resp):
        print(f"Response: {resp.status_code}")

app.add_middleware(SimpleCustomMiddleware)
```









    