# Intro to Web Development with Flask
_By Mohammad Mahmoud Khajah (mmkhajah@kisr.edu.kw)_

# Application Overview

We will be developing a reading group application similar to the one I did for [SSDD's reading group](https://www.lambda-complex.com/ssdd/). The application will support the following features:

* Users can view the list of scheduled presentations
* Users can view the list of presentations suggested but not yet scheduled
* Users can see the details of a presentation: who's presenting, what time, title of presentation, attachments, etc.
* Admins can add, edit, and remove presentations.
* Admins can upload attachments with presentations. 

The requirements are simple, but they are enough to cover everything we need to talk about during this course:

* Templates
* Static files
* Routing
* Persistence
* Authentication and Authorization
* Forms
* File uploads
* Deployment

# Web Application Architecture

A web application consists of a _client-side_ and a _server-side_. The client-side typically executes on the web browser and consists of HTML/CSS/Javascript, while the server-side executes on a server and can be written in any language. A mobile app is another example of a client and it can also be written in any language. In this course however, we focus on web browser clients.

The flow of a web application is as follows:

1. The user enters a URL into their web browser.
2. If the URL is a domain name, the browser asks the Domain-Name-System (DNS) server for the IP address that corresponds to the domain name.
3. Given the IP address, the browser makes an HTTP request. Server applications always listen on a _port_ which is a number that helps the server OS decide which connections should be handled by which piece of software. If the user does not specify a port in the URL, the browser assumes it is port 80.
4. The server recieves the request, processes it, and returns a response. Typically the response is an HTML page.
5. The browser displays the server's response. 
6. The user further interacts with the server through elements on the HTML page (e.g., forms, links, etc.). Each interaction is a new http request.

An important factor to remember is that the HTTP protcol is **stateless**: each HTTP request is treated in isolation, without regard to the history of requests that came before it. In other words, the web server does not keep a list of actively connected clients nor does the client keep a list of actively connected servers.  This simplifies protocol design at the cost of having the application developer (you) keep extra information to track a user between requests. For example, you may have heared of _cookies_ 🍪 which are little nuggets of data that the browser sends with every request to the server. The server can store data in these cookies, e.g., shopping cart contents, so that it can track users between requests.

Most of the action in this course occurs in the server-side (step 4): receiving a request and generating a response. Many tasks in server-side development are repetitive: read input data, validate forms, communicate with a database, render the output, etc. To keep developers focused on the application’s main features, many frameworks have been created to automate common tasks, e.g., ASP dot NET MVC, Ruby on Rails, Django, etc. While it is easy to get started with many of these frameworks, developers will often have a hard time diagnosing issues because so much detail is hidden away in the framework’s source code. In this course, we will instead introduce programmers to a simple Python web framework called Flask which provides solid support for the developer without introducing layers of abstraction that get in the way. 

# Installation

## Mac

(instructions lifted from https://wsvincent.com/install-python3-mac/)

```sh
$ xcode-select --install
$ /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
$ brew doctor
Your system is ready to brew
$ brew install python3
$ python3 --version
Python 3.7.0
```

Create a course directory and setup the virtual environment for this course:
```sh
$ mkdir ~/webdev-course
$ cd ~/webdev-course
$ python3 -m venv venv
$ . venv/bin/activate
$ pip install wheel
$ pip install Flask
```

Whenever you open a new terminal window, you will have to activate the virtual environment:
```sh
$ cd ~/webdev-course
$ . venv/bin/activate
...
$ deactivate # to deactivate
```

## Windows

1. Install [Anaconda Python 3.7 Windows x64](https://www.anaconda.com/distribution/#download-section)
2. After installation, open a terminal and run:
```cmd
C:\Users\Mohammad> conda create -n myenv
C:\Users\Mohammad> activate myenv
(myenv) C:\Users\Mohammad> conda install flask
```
3. Create a directory for the course:
```cmd
C:\Users\Mohammad> mkdir webdev-course
C:\Users\Mohammad> cd webdev-course
```

When you open a new terminal window, you will have to activate the virtual environment:
```cmd
C:\Users\Mohammad> activate myenv
```

# Basic Flask App

Flask applications can be written in a single Python file. Let's work through a simple app:

1. Under the course directory, create a subdirectory called `hello-world`
2. Within the subdirectory create a new file called `hello-world.py` with the following content:
```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'
```
* import the `Flask` class into the script's namespace. If we had only written `import flask` then we'd have to write `flask.Flask` to refer to the Flask class.
* create an instance of a `Flask` application. The first argument to the `Flask` constructor is the name of the module or package where your application resides. For a single module Flask app, like this one, always use the special variable `__name__` which will contain the name of the currently executing module.
* create function called `hello_world` which takes no arguments and returns a string
* we _decorate_ the function with a Flask routing decorator which indicates which URL should trigger the decorated function. 

We'll get to what decorators are shortly, but first let's run the app (on Windows use `set` instead of export):

```sh
$ export FLASK_APP=hello-world.py
$ export FLASK_ENV=development
$ flask run
```

* The `export` lines set _environment variables_. Environment variables are key/value pairs that are made available to all programs executed within the current environment.  The `PATH` variable, which is a list of places where programs can find executables, is a famous example of an environment variable. Note that environment variables are set per terminal, so if you launch another terminal, you'd have to re-set them.
* `FLASK_APP` tells flask which module to run and `FLASK_ENV` activates debugging mode, which prints helpful debugging messages in the browser window, and enables the automatic reloader, which reloads files upon any changes.
* `flask run` launches the development server.

Now open your web browser and navigate to `http://localhost:5000`. You should see the message "Hello, World!".
Let us add another page to the application:

```python
@app.route('/another_page')
def another_page():
    return 'Another page!'
```

Navigate to `http://localhost:5000/another_page`. You should see "Another page!" in the browser's window.

> Exercise: change `another_page():` to `another_page()5463456` and reload the url. See what happens.

## Decorators

Python treats functions as first-class objects: they can be passed around and stored in variables. To understand how decorators work, let us look at a few examples. 

1. Create a file called `decorators.py`, we'll explore how decorators work in this file.
```python
def greet(name):
    return "Hello %s" % name

print(greet("Noura"))
```
2. Run: `python decorators.py`, it should print `Hello Noura`

Now, suppose we wish to modify the function so that it puts HTML `<strong>` tags around the greeting message. We can modify the function itself, by manually adding HTML to the greeting string, but that would violate the single responsibility principle: a function should do one thing and do it really well. Instead, we'll use function composition:

```python
def greet(name):
    return "Hello %s" % name

def strong(func):
    def wrapper(name):
        return "<strong>" + func(name) + "</strong>"
    return wrapper

greet = strong(greet)

print(greet("Noura"))
```

* The `strong` function accepts a single argument, `func`, and
defines a nested function, `wrapper`, which accepts a `name` argument. 
* `wrapper` assumes that the `func` argument references a callable object (a function). It calls the function referenced by `func` and wraps the result in the `<strong>` tag.
* `strong` returns `wrapper`.
* The expression `strong(greet)` calls `strong`, passing the function `greet` to it. This expression returns the `wrapper` function, which is then assigned to the name `greet`.

Re-running this code will produce a greeting wrapped in `<strong>` tags. This is pretty powerful: the greeting function does not need to know anything about returning HTML, and the strong function does not need to know about greetings. We say that `strong` is a _decorator_.

Python provides syntactic sugar to make it easier to specify decorators on functions. The previous example would be:

```python
def strong(func):
    def wrapper(name):
        return "<strong>" + func(name) + "</strong>"
    return wrapper

@strong
def greet(name):
    return "Hello %s" % name
print(greet("Noura"))
```

It is possible to define multiple decorators on one function: 

```python
@dec1
@dec2
def some_func(arg1, arg2):
    ...
```

This would correspond to doing `some_func = dec2(dec1(some_func))`. It is also possible to pass arguments to decorators but your head will explode&mdash;you need three levels of functional nesting:

```python
def strong(className):
    def strong_decorator(func):
        def wrapper(name):
            return "<strong class='%s'>%s</strong>" % (className, func(name))
        return wrapper
    return strong_decorator

@strong("large-font")
def greet(name):
    return "Hello %s" % name

print(greet("Noura"))
```

Back to our context: the `app.route(url)` decorator essentially associates the decorated function with the specified url on the app object. In such a scenario, the purpose of the decorator is not to wrap the function, but to use it in some way.

You can find more about decorators in this [article](https://www.thecodeship.com/patterns/guide-to-python-function-decorators/).

# Generating the List of Presentations

Our first requirement is to generate a list of scheduled presentations. 

First, we'll create some data to work with. We'll be using the SQLite database which is a nice small self-contained database library. An SQLite database is just a single file; there is no server configuration to worry about or permissions to assign. 

## Creating the Database

1. Create a subdirectory called `rgs` under the course's directory.
2. Create the database schema + seed file `schema.sql`:
```sql
DROP TABLE IF EXISTS presentation;
CREATE TABLE IF NOT EXISTS presentation (
    id integer PRIMARY KEY AUTOINCREMENT,
    title text NOT NULL,
    presenters text NOT NULL,
    scheduled date DEFAULT null,
    time_range text DEFAULT '',
    notes text NOT NULL DEFAULT ''
);
INSERT INTO presentation VALUES (null,'Dynamic Key-Value Memory Networks for Knowledge Tracing','Mohammad','2018-05-21','10-11am','');
INSERT INTO presentation VALUES (null,'Comparison of Indoor Air Quality in Schools: Urban vs. Industrial ''Oil & Gas'' Zones in Kuwait','Dr. Ali Al-Hemoud','2018-05-30','9:30-10am','');
INSERT INTO presentation VALUES (null,'Long-Term Spatiotemporal Analysis of Social Media for Device-to-Device Networks','Muneera & Megha','2018-05-30','10-11am','<a href="https://gist.github.com/mmkhajah/ae2b3421ec4bcb2bd3ecb9a2bf928cdb">The problem with Fig. 1</a>');
```
It is common for SQL tables to have a unique key for a every row. When inserting new data, we want this key to be automatically generated, which why we specify `null` as the key value in the `INSERT` statements.

3. Create and execute the following python script, `initdb.py`, to generate the database:
```python
import sqlite3
db = sqlite3.connect('db.sqlite', detect_types=sqlite3.PARSE_DECLTYPES)
script = open('schema.sql', 'r').read()
db.executescript(script)
db.close()
```
Python comes bundled with `sqlite3`, a library that manipulates SQLite databases. The `sqlite3.connect()` function establishes a connection to a new or existing database. The `PARSE_DECLTYPES` constant tells the library to convert column types, such as number, text, and date, to the corresponding Python types. After executing this script, the `db.sqlite` file should appear in `rgs`.

> ### Keyword Arguments
> Python supports specifying function arguments as key/value pairs. For example,
> ```python
> def add(a, b, c):
>   return a + b + c
> add(3, 4, 5)
> add(3, 4, c = 5)
> add(a=3, b=4, c=5)
> add(a=3, 4, 5) # invalid syntax

## Adding the List View

1. Create `rgsapp.py`:
```python
from flask import Flask
import json
import sqlite3

app = Flask(__name__)
app.config['db_path'] = 'db.sqlite'

@app.route('/')
def home():
    
    db = connect_db()
    
    presentations = db.execute("select * from presentation")
    
    output = "<ul>"
    for p in presentations:
        output += "<li>%s</li>" % (p['title'])
    output += "</ul>"
    
    db.close()
    
    return output
    
def connect_db():
    
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
    
    db = sqlite3.connect(app.config['db_path'],
                         detect_types=sqlite3.PARSE_DECLTYPES)
    db.row_factory = dict_factory
    return db
```

* The `config` instance member variable of the `app` object stores application configuration. Complex apps will have many variables (e.g., where the database is, security settings, etc.) and will likely load their configuration from a file on disk. In our case, we just have one variable: where to find the database file. It is a good idea to use configuration variables so that you don't hardcode them in main application code. Regardless of where the configuration is loaded from, the settings will be available in the `config` instance member.
* By default, `sqlite3` returns database rows as arrays, so `row[0]` corresponds to the first column, and so on. This is very inconvenient; instead we set a custom `row_factory` which is a function that takes a row and transforms it. In our case, the function transforms the row into a dictionary where keys and values are column names and values, respectively.
* the code loops through every presentation and generates a bulleted HTML list containing the title of the presentation.
* Calling `execute` on the database object returns an iterator over the resulting rows. Note that it does not return a list: if you want a list, you'll have to wrap the call: `list(db.execute(...))`. An iterator does not store the whole list of rows in memory; it walks the list of rows one-by-one, so it is more memory-efficient.

2. In the terminal:
```sh
$ export FLASK_APP=rgsapp.py
$ flask run
```
and navigate to `127.0.0.1:5000` in your browser. You should see a bulleted list of presentation titles.

The data is crying to be in a table, so let's use a `<table>` tag to show extra details on each presentation. Replace the output lines in the previous code with:

```python
output = "<h1>Scheduled Presentations</h1>"
output += "<table>"
output += "<thead>"
output += "<tr>"
output += "<td width='20%'>Date &amp; Time</td>"
output += "<td width='50%'>Title</td>"
output += "<td width='30%'>Presenters</td>"
output += "</tr>"
output += "</thead>"
output += "<tbody>"
for p in presentations:
    output += "<tr>"
    output += "<td>%s %s</td>" % (p['scheduled'], p['time_range'])
    output += "<td>%s</td>" % (p['title'])
    output += "<td>%s</td>" % (p['presenters'])
    output += "</tr>"
output += "</tbody></table>"
```
Refresh the page in the browser, you should now see the data in a tabular format.

Generating HTML directly from the code gets unwieldy very quickly. The problem is that most of the HTML is really just constant and constants should not be embedded directly into code. Fortunately, Flask has a solution: the `Jinja` template library. Templating in general refers to replacing placeholders in a string. For example, you've already used a simple form of templating when you wrote `"<td>%s</td>" % (p['title'])`. The Jinja library extends this basic concept with useful control structures, extension mechanisms, macros, etc. We'll move the code we just wrote into a template:

1. Create a folder called `templates` under `app-templates`
2. Create a file `home.html` under `templates` and put the following into it:

```html
<!doctype html>
<html>
 <head>
  <meta charset='utf-8'>
  <title>List of Presentations</title>
  <link rel='stylesheet' href='{{ url_for("static", filename="css/style.css") }}' type="text/css">
 </head>
 <body>
  <h1>Scheduled Presentations</h1>
  <table>
   <thead>
    <tr>
     <th width="20%">Date &amp; Time</th>
     <th width="50%">Title</th>
     <th width="30%">Presenters</th>
    </tr>
   </thead>
   <tbody>
    {% for p in presentations %}
    <tr>
     <td class='centered-text'>{{ p['scheduled'] }}<br>{{ p['time_range']  }}</td>
     <td><strong>{{ p['title'] }}</strong></td>
     <td  class='centered-text'>{{ p['presenters'] }}</td>
    </tr>
    {% endfor %}
   </tbody>
  </table>
 </body>
</html>
```

The file is mostly just normal static HTML, but with some special "sauce" added to it:

* `{% ... %}` corresponds to Jinja statements. These are typically control structures (if/else, loops, etc.), include statements (to include one template into another), and extend statements (for template inheritance).
* `presentations` is a variable that exists within the template's _context_. You control what gets passed into this context from Python. We'll get to that shortly.
* we access the attributes of each presentation `p` just like we do in Python.
* `{{ ... }}` prints the expression inside it to the output.

While some of the expressions inside `{% ... %}` and `{{ ... }}` look like Python code, they are **NOT** Python. So don't go around trying to execute arbitary code there. Complicated logic belongs to  application code, not in templates.

3. Modify `rgsapp.py`:
```python
from flask import Flask, render_template

...

@app.route('/')
def home():
    db = connect_db()
    
    presentations = db.execute("select * from presentation")
    
    output = render_template('home.html', presentations=presentations)
    
    db.close()
    
    return output
```
* The `render_template` function is imported from the `flask` module. It is used render Jijna templates.
* Remember the `presentations` variable in `home.html`? we make it available in the template's context by assigning the `presentations` variable to the keyword argument `presentations` of the function `render_template`.
* `render_template` accepts the template's file name as the first argument. It will look for it in the `templates` folder by default. The function returns the rendered template as a string.

If you refresh your browser, you should see the same output as before. Let's prettify the interface a bit and flex our CSS muscles. 

1. Create a directory  `static` under `rgs`, and create a directory `css` under `static`.
2. Create a file `style.css` under `css`:

```css
html {
    box-sizing: border-box;
    height: 100%;
    font-size: 14pt;
}
*, *:before, *:after {
    box-sizing: inherit;
}

body {
    margin: 0;
    padding: 10px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol";
}

h1, h2, h3 {
    color: DodgerBlue;
}

table {
    width: 100%;
    border-collapse: collapse;
}

td, th {
    border: 1px solid black;
    padding: 5px;
    vertical-align: top;
}

th {
    background: DodgerBlue;
    color: white;
}

.centered-text {
    text-align: center;
}

.form-errors {
    color: red;
}

.btn-txt {
    font-size: 1.25rem;
    text-decoration: none;
    color: #333366;
    font-weight: bold;
}
```
3. Go back to `home.html` and add the following line to the `<head>` section:

```html
<link rel='stylesheet' href='{{ url_for("static", filename="css/style.css") }}' type="text/css">
```
We don't know what the URL of the application will be; during development it is `localhost` and during production it will be something else. The `url_for()` function, which Flask [makes available by default](http://flask.pocoo.org/docs/1.0/templating/) in the template's context, resolves this problem by  inserting the URL of the application during runtime. The function takes the name of an _endpoint_ and, in this case, the filename to generate a URL for. Endpoints are actions that the Flask app makes available; in our app, `home` is one such endpoint.  The `static` endpoint is a special handler for static files&mdash;files which are delivered as-is to the client. In this case, the filename we want to generate a URL for is the CSS stylesheet.

> **Tip**: changes to CSS files, images, and other static resources may not be seen by the browser. In those cases, hit `shift+F5` to force a hard refresh and reload everything.

# Adding a Second Route: Presentation Details
Presentations may have extra pieces of information, such as notes or short abstracts, and we want to display those when users click on a presentation from the list. So let's add a page which shows presentation details:

1. Add a new template file, `details.html`:
```html
<!doctype html>
<html>
 <head>
  <meta charset='utf-8'>
  <title>Presentation: {{ p['title'] }}</title>
  <link rel='stylesheet' href='{{ url_for("static", filename="css/style.css") }}' type="text/css">
 </head>
 <body>
  
  <h1>Presentation Details</h1>
  
  <ul>
   <li><strong>Title:</strong> {{ p['title'] }}</li>
   <li><strong>Presenter(s):</strong> {{ p['presenters'] }}</li>
   <li><strong>Date and Time:</strong> {{ p['scheduled'] }} {{ p['time_range'] }}</li>
  </ul>
  
  <h2>Notes</h2>
  {{ p['notes'] }}
  
 </body>
</html>
```

2. In `rgsapp.py`, add the `details` view:
```python
from flask import Flask, render_template, abort
...
@app.route('/presentation/<int:pid>')
def details(pid):
    
    db = connect_db()
    presentation = db.execute("""select * from presentation p where p.id = ?""", (pid,)).fetchone()

    if presentation is None:
        abort(404)
    
    db.close()
    
    return render_template('details.html', p=presentation)
```
* `abort` terminates request processing and returns with HTTP status 404 (not found). In real life, you'd probably want to define your own 404 template, but this is good enough for now.
* Since each presentation has a different ID, we cannot use a constant route for the `details` view function. Instead, we use a _variable rule_ to match the ID in the URL to the view function. The pattern `/presentation/<int:pid>` tells the router to pass the value at the end of the URL as a keyword argument called `pid` to the `details` view function. It also instructs the router to convert the value to an `int` type. If Flask is unable to coerce the value into an `int`, it will return a 404 before ever executing the view function.

3. Navigate to `localhost:5000/presentation/3`, you should see details on Muneera & Megha's presentation. But something peculiar happens: the HTML code in `p['notes']` is being shown as text rather than a link&mdash;it is being _escaped_. By default, Jijna escapes all variables for security reasons because you don't want malicious users injecting evil HTML into your website. But, if you are confident that the source of HTML is safe, you can tell Jijna so through a _filter_:
```html
{{ p['notes'] | safe }}
```
Filters modify the variable on the left side of the pipe. They are functions that accept the variable on the left as the first argument and return a transformed version. In this case, the `safe` filter tells Jinja not to escape the HTML code in the variable. Jinja has a [bunch of other useful filters](http://jinja.pocoo.org/docs/2.10/templates/#builtin-filters). Refresh your browser page and you should see the expected link. But before moving on, verify that you get a 404 page when you use an incorrect id.

We need to add links from the home view to each presentation's details page. Open `home.html` and replace the line 
```html
<td><strong>{{ p['title'] }}</strong></td>
```

with
```html
<td><a href="{{ url_for('details', pid=p['id']) }}"><strong>{{ p['title'] }}</strong></a></td>
```
The `url_for` function strikes again! this time, the endpoint is the `details` function. Since the `details` function expects an argument called `pid`, we pass an argument with the same name to the `url_for` function. The cool thing is that the function will generate a URL that matches the pattern given in the route decorator of `details` view. Navigate to `localhost:5000` to see the result.

You might have noticed that `home.html` and `details.html` templates share a lot in common as both of them have nearly identical header sections. As good programmers, we strive to eliminate duplication. Fortunately, Jinja provides a mechanism called template inheritance which allows you to define a base template that "child" templates can override parts of. 

1. Create a file  `base.html`:
```html
<!doctype html>
<html>
 <head>
  <meta charset='utf-8'>
  <title>{% block title %}Default Title{% endblock %}</title>
  <link rel='stylesheet' href='{{ url_for("static", filename="css/style.css") }}' type="text/css">
 </head>
 <body>
  
  <h1>{{ self.title() }}</h1>
  
  {% block content %}{% endblock %}
  
 </body>
</html>
```
This file will serve as the basic wrapper of other templates. The `{% block name %}...{% endlbock %}` statements define where the children can inject content. If the child does not override the block, the value in the parent template will be used (e.g., `Default Title` in the code above). We want to put the title in the page header and in the body, but Jinja does not allow multiple blocks of the same name in the same template. So we use `{{ self.title() }}` to tell Jinja to inject the value of the `title` block where the expression appears. 

2. Modify `home.html`:
```html
{% extends 'base.html' %}

{% block title %}Scheduled Presentations{% endblock %}

{% block content %}
<table>
 <thead>
  <tr>
   <th width="20%">Date &amp; Time</th>
   <th width="50%">Title</th>
   <th width="30%">Presenters</th>
  </tr>
 </thead>
 <tbody>
  {% for p in presentations %}
   <tr>
    <td class='centered-text'>{{ p['scheduled'] }}<br>{{ p['time_range']  }}</td>
    <td><a href="{{ url_for('details', pid=p['id']) }}"><strong>{{ p['title'] }}</strong></a></td>
    <td  class='centered-text'>{{ p['presenters'] }}</td>
   </tr>
  {% endfor %}
 </tbody>
</table>
{% endblock %}
```

3. Modify `details.html`:
```html
{% extends 'base.html' %}

{% block title %}Presentation: {{ p['title'] }}{% endblock %}

{% block content %}
<ul>
   <li><strong>Title:</strong> {{ p['title'] }}</li>
   <li><strong>Presenter(s):</strong> {{ p['presenters'] }}</li>
   <li><strong>Date and Time:</strong> {{ p['scheduled'] }} {{ p['time_range'] }}</li>
  </ul>
  
<h2>Notes</h2>
{{ p['notes']|safe }}
  
{% endblock %}
```
Both templates inherit from `base.html` and override the parent's blocks. 

# Our First Form: Creating a Presentation

1. Create a new template `create.html` with the following content:

```html
{% extends 'base.html' %}

{% block title %}Add a Presentation{% endblock %}

{% block content %}
<form method="post">

<dl>
    <dt><label for="title">Title</label></dt>
    <dd><input id="title" name="title" required type="text" value=""/></dd>

    <dt><label for="presenters">Presenter(s)</label></dt>
    <dd><input id="presenters" name="presenters" required type="text" value=""/></dd>

    <dt><label for="scheduled">Date</label></dt>
    <dd><input id="scheduled" required  name="scheduled" type="date" value=""/></dd>

    <dt><label for="time_range">Time</label></dt>
    <dd><input id="time_range" required  name="time_range" type="text" value=""/></dd>
    
    <dt><label for="notes">Notes</label></dt>
    <dd><textarea name="notes" cols="40" rows="5">{{ request.form['notes'] }}</textarea></dd>
    
</dl>

<p><input type="submit" value="Add"/></p>

</form>
{% endblock %}
```
The `form` tag has a `post` method because we intend to change the data on the server. There are two common methods in the HTTP protocol: `GET` and `POST`, information submitted over `GET` is directly encoded into the request URL (as query string parameters, e.g., `search?keywords=hello+world`), while data submitted over `POST` is included in the body of the HTTP request. For this reason, `GET` requests should only be used to retrieve information, while `POST` requests should be used for operations that cause side-effects.

Each form field we want to submit should have a `name` attribute so that the server can access it. Some fields have a `required` attribute which lets the browser do some basic validation checks which otherwise would need to be done in Javascript (yay!).

2. Add a new route for the creation form in `rgsapp.py`:
```python
@app.route('/create', methods=('GET', 'POST'))
def create():
    return render_template('create.html')
```
By default, Flask views only accept `GET` requests. Here, we tell it to allow `POST` requests as well on the `create` view.

3. Navigate to `localhost:5000/create` and you should see the new creation form. Enter some information and hit "Add". Play with the browser validation by leaving out the required fields. When you submit, you will see that you get the same empty form again. This is expected because the `create` view only shows an empty form. Let's change that so that it saves submissions:
```python
from flask import Flask, render_template, abort, request, redirect, url_for
...
@app.route('/create', methods=('GET', 'POST'))
def create():

    if request.method == 'POST':
        
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("""insert into presentation(title, presenters, scheduled, time_range, notes)
            values(?, ?, ?, ?, ?)""", 
            [request.form[f] for f in 
            ('title', 'presenters', 'scheduled', 'time_range', 'notes')])
        
        db.commit()
        db.close()
        return redirect(url_for('home'))
    
    return render_template('create.html')
```
* It is common practice to have a form view like `create` handle both `GET` and `POST` requests.
* If the request is `POST`, we insert the new presentation into the database. Notice that we are using the _placeholder_ syntax in the `cursor.execute()` function, where the values to be inserted are replaced with question marks. The actual values are supplied as a list in the second argument. This allows the library to secure the inserted values and protect you from SQL Injection attacks. 
* `commit()` saves the changes to the database
* `redirect(url)` tells the browser to navigate to `url`. So in this case, we're telling the browser to navigate to the `home` view. Make no mistake about what is happening here: you are not calling the `home` function directly; rather, Flask is telling the browser to navigate to a new URL, and it is the browser which will then make a new request to the `home` view.

What if the form is missing some fields? for example, if the field `title` does not exist in the form, then `request.form['title']` will raise an exception and Flask will return a 400 Bad Request error, which is good because missing fields may indicate that any attacker is trying to bypass the user interface and send data directly, so we don't need to show them a friendly error page.

Fill out the form and click submit, you should be redirected to the home screen and you should be able to see the new presentation's details, though the lack of confirmation is jarring: the user has no idea if the operation was successful or not and he or she would have to scan the list of presentations to confirm that the presentation has been added. 

A nice UI pattern that solves the lack of feedback is to show a _flash message_ on the home page that only appears after a successful form submission and disappears afterwards. The problem though is how to show the message: remember, Flask is redirecting the browser to the home page; so how would the `home` view know to show a confirmation message or not? the answer is with a cookie 🍪. 

Cookies are small containers (4KB max) of data that are exchanged between the browser and the server. They are sent to the server on every request and can be manipulated both on the server (Flask) and the client sides (i.e., from Javascript on the browser). So how are cookies useful for flashing messages? the idea is to set a cookie before redirecting the browser, and then to have the `home` view read it&mdash;like a boomerang cookie. So let's do it:

1. Add `flash` to the list of names important from the `flask` module in `rgsapp.py`
2. Add the following just before the `redirect()` function call in the `create` view:
```python
flash('Presentation has been added')
```
This statement will append a message to the list of flash messages in the cookie that is sent back to the client.

3. add the following to the base template `base.html`:
```html
  {% with messages = get_flashed_messages() %}
   {% if messages %}
    <ul class='flashes'>
    {% for message in messages %}
      <li>{{ message }}</li>
    {% endfor %}
    </ul>
   {% endif %}
  {% endwith %}
```
The `{% with %}` Jinja statement establishes an _inner scope_. All variables defined within that scope will not be available outside it. In this example, the `messages` variable will not be available after `{% endwidth %}`. The `get_flashed_messages()` function is another function that Flask makes available by default in the template's context. It retrieves the list of flash messages from the cookie. We then display this list with standard Jinja statements.

If you try to create a new presentation and hit submit, you will see a `RuntimeError: The session is unavailable because no secret key was set`. Flask implements `sessions` which persist user information across requests. However, for security purposes, Flask _signs_ the cookies via secret key. Signing refers to computing a hash&mdash;the signature&mdash;of the value of the cookie, using the secret key. When the cookie is sent to the server, Flask hashes the received value and compares it against the signature. If they do not match, Flask discards the request. In short, we need to define a hard secret key for our app to use when signing cookies. Add the following to `rgsapp.py`:
```python
app.secret_key = b'xYFRlEs3@a'
```
Note this is key is weak, but for demo purposes it should be fine. The `b'...'` syntax corresponds to a _byte literal_ in Python which can only contain ASCII characters. In real life, make sure that (a) the secret key is long and hard to guess, and (b) store it somewhere **outside** of source control tree (don't commit it to github).

Now, retry creating a presentation. You should be redirected to `home` view and you will see the "Presentation has been added" message. If you refresh the home page, the flashed messages disappear, which is the intended behavior.

> ## Why the hassle? 
> You may be wondering, why don't we just call the `home` function directly, rather than issue a redirect. We'd avoid dealing with sessions and cookies but consider what happens if you refresh the home page after submitting the form. The browser will prompt the user to "resend the data" because it thinks he or she are trying to refresh the form. By redirecting the browser, we are telling the client that the form submission is complete.

# Validating Inputs

We need to ensure that users are entering proper inputs into the forms (e.g., inputs are not too short, correct date format is provided, numbers are within range, etc.). While the browser can provide basic input validation, you should **never** rely on browser-side validation as it can easily be bypassed (even if you have a bit of custom Javascript that does validation on the client-side). All inputs must be validated on the server-side. 

The input validation process is as follows:
1. If the request is `POST`, validate the form inputs
2. If there are errors during validation, re-display the form with the validation errors *and* the fields that have already been filled so that the user doesn't have to enter them again.
3. If there are no errors, save and redirect as usual
4. If the request is GET, display the form.

## The Manual Way
So let's implement the necessary changes:

1. update the `content` block `create.html` as follows:
```html
{% if errors %}
<ul class='form-errors'>
 {% for e in errors %}
  <li>{{ e }}</li>
 {% endfor %}
</ul>
{% endif %}

<form method="post">

<dl>
    <dt><label for="title">Title</label></dt>
    <dd><input name="title" required type="text" value="{{ request.form['title'] }}"/></dd>

    <dt><label for="presenters">Presenter(s)</label></dt>
    <dd><input name="presenters" required type="text" value="{{ request.form['presenters'] }}"/></dd>

    <dt><label for="scheduled">Date</label></dt>
    <dd><input name="scheduled" type="date" required value="{{ request.form['scheduled'] }}"/></dd>

    <dt><label for="time_range">Time</label></dt>
    <dd><input name="time_range" type="text" required value="{{ request.form['time_range'] }}"/></dd>
    
    <dt><label for="notes">Notes</label></dt>
    <dd><textarea name="notes" cols="40" rows="5">{{ request.form['notes'] }}</textarea></dd>
</dl>

<p><input type="submit" value="Add"/></p>

</form>
```
We've added a block that lists any errors, and we've 
pre-populated form inputs with request form values. The `request` object is another object that Flask makes available by default in the template's context.  Notice how we stripped the `safe` filter for the notes input; we really want just text in the textarea, no active HTML.

2. Add the following function to the end of `rgsapp.py`:
```python
def validate_onsubmit():
    if request.method == 'GET':
        return False, []
    
    f = request.form
    
    errors = []
    
    if len(f['title']) < 4:
        errors.append('Title has to be at least 4 characters long')
    if len(f['presenters']) < 4 or re.search(r'\d', f['presenters']):
        errors.append('Presenters has to be at least 4 alphabetical characters long')
    if not re.match(r'\d{4}\-\d{2}\-\d{2}', f['scheduled']):
        errors.append('Date needs to be YYYY-MM-DD')
    if not range_regex.match(f['time_range']):
        errors.append('Time range should be like 9-10am, 9:30-11:40, etc.')
    
    is_valid_submission = len(errors) == 0
    return is_valid_submission, errors
```
3. near the top of the file, add the following:
```python
import re

range_regex = re.compile(r"^(?P<fromhour>\d{1,2})\s*(:\s*(?P<fromminute>\d{1,2}))?\s*(?P<fromampm>am|pm)?\s*\-\s*(?P<tohour>\d{1,2})\s*(:\s*(?P<tominute>\d{1,2}))?\s*(?P<toampm>am|pm)?$", flags=re.IGNORECASE)
```
* The `validate_onsubmit` function returns two things: whether a valid form has been submitted, and the list of errors if any. The function uses regular expressions functionality from Python's `re` module. The Regular expressions language is a specialized pattern-matching tool that originated from Perl. Whole books have been written on them and so discussing them is beyond the scope of this course. Just as an example though, `r'\d{4}\-\d{2}\-\d{2}'` matches four digits, followed by a dash, followed by two digits, followed by dash, and followed by two digits. The `r'...'` syntax defines a Python _raw_ string, which interprets the string as-is: backslashes `\` do not need escaping and escape sequences such as newlines `\n` are not replaced. Raw strings are commonly used for regular expressions because regexes make heavy use of backslahes. 

4. Modify the `create` view:
```python
def create():
    
    is_valid_submission, errors = validate_onsubmit()
    
    if is_valid_submission:
        ...

    return render_template('create.html', errors=errors)
```
Try to create a form with a presentation title that is too short, or add numbers to the list of presenters. You will see the corresponding error messages and you will notice that the form remembers what the user has entered. Fix the problems and try to resubmit, the presentation will be aded.

## The WTForms Way
Input validation is such a common task in web development that many libraries have been developed to streamline it. Python's `WTForms` is the default choice for many Flask users, so Flask developers have created an even easier-to-use form validation library based on `WTForms` called `Flask-WTF`.

1. Install `Flask-WTF` with `pip install Flask-WTF` or `conda install flask-wtf`

2. Create `forms.py`:
```python
from flask_wtf import FlaskForm
from wtforms import StringField, FileField, validators, widgets, Field, HiddenField
from wtforms.fields.html5 import DateField
import re

vals = validators
range_regex = re.compile(r"^(?P<fromhour>\d{1,2})\s*(:\s*(?P<fromminute>\d{1,2}))?\s*(?P<fromampm>am|pm)?\s*\-\s*(?P<tohour>\d{1,2})\s*(:\s*(?P<tominute>\d{1,2}))?\s*(?P<toampm>am|pm)?$", flags=re.IGNORECASE)

range_validator = vals.Regexp(range_regex,
                                    message='Time range format is invalid. Examples of valid inputs are 11-1pm, 10:30am-11:00am, etc.')
class PresentationForm(FlaskForm):
    
    title = StringField('Title', validators=[vals.Length(min=4, message="Title has to be at least 4 characters long")])
    presenters = StringField('Presenter(s)', validators=[
        vals.Length(min=4, message="List of presenters has to be at least 4 alphabetical characters long"), 
        vals.Regexp(r'^[a-zA-Z\s&\-\.]+$', message="Only alphabetical characters are allowed in the presenters list")
    ])
    scheduled = DateField('Date', validators=[vals.DataRequired()])
    time_range = StringField('Time', validators=[vals.DataRequired(), range_validator])
    notes = StringField('Notes', widget=widgets.TextArea())
```
* We define a class that inherits from the `FlaskForm` class, which provides useful functions for form validation.
* We define the fields in our form as _class_ attributes. Unlike _instance_ attributes (e.g., `player.x = 45`) which are defined on a per-instance basis, class attributes are *shared* across all instances of a class. For example,
```python
>>> class foo:
>>>    x = 3
>>> a = foo()
>>> b = foo()
>>> a.x
3
>>> b.x
3
>>> foo.x = 54 # to set a class attribute, you have to refer to the class by name
>>> a.x
54
>>> b.x
54
>>> a.x = 98 # this creates an _instance_ attribute, masking the class one
>>> b.x
54
```
* `WTForms` provides several classes that correspond roughly to HTML form fields. The `StringField` for example, corresponds to an `<input type="text">` field by default. Each field class takes a title field which will get dispalyed on the form, and a list of validator objects to run against the field's value. `WTForms` provides useful validator classes: `Length` ensures that the length of the input is within a minimum and/or maximum, `DataRequired` ensures that the user has entered a value, and `Regexp` verifies that the input matches a regular expression pattern. In this code, we are calling the constructors of these validators to create validator objects. Each constructor takes a `message` argument which gets displayed when there is an error in the validation. Notice how we supply a `TextArea` widget to the `notes` field because we want to show that field as a `<textarea>`.
3. Change `rgsapp.py`:
```python
from forms import PresentationForm
...
@app.route('/create', methods=('GET', 'POST'))
def create():
    form = PresentationForm()
    
    if form.validate_on_submit():
        
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("""insert into presentation(title, presenters, scheduled, time_range, notes)
            values(?, ?, ?, ?, ?)""", 
            [getattr(form, f).data for f in 
            ('title', 'presenters', 'scheduled', 'time_range', 'notes')])
        
        db.commit()
        db.close()
        
        flash('Presentation has been added')
        return redirect(url_for('home'))
    
    return render_template('create.html', form=form)
```
* We import and instantiate the `PresentationForm`. The form class knows to automatically use the `request` object that Flask provides to get form data.
* `validate_on_submit()` returns `True` if the request is `POST` and all fields are valid, and `False` otherwise.
* The class attributes we defiend in `PresentationForm` contain submission data, but we cannot access them dynamically with `form[f]`. To access object attributes in Python dynamically, use the `getattr(obj, attrname)` function.
* Each class attribute in `PresentationForm` has a `data` attribute which contains the submitted value. We can use the `request.form[f]` as before but sometimes, the form class will do extra _sanitization_ on the submitted values so it is a good idea to use the value in the form, not the request.
* We deliver the `form` itself to the template context so that we can display fields and show errors.

4. Change the `create.html` template:
```html
{% macro render_field(field) %}
  <dt>{{ field.label }}</dt>
  <dd>{{ field(**kwargs)|safe }}
  {% if field.errors %}
    <ul class="form-errors">
    {% for error in field.errors %}
      <li>{{ error }}</li>
    {% endfor %}
    </ul>
  {% endif %}
  </dd>
{% endmacro %}

{% extends 'base.html' %}

{% block title %}Add a Presentation{% endblock %}

{% block content %}

<form method="post">
{{ form.csrf_token }}
<dl>
    {{ render_field(form.title) }}
    {{ render_field(form.presenters) }}
    {{ render_field(form.scheduled) }}
    {{ render_field(form.time_range) }}
    {{ render_field(form.notes) }}
</dl>

<p><input type="submit" value="Add"/></p>

</form>

{% endblock %}
```
* We define a Jinja _macro_ which is similar to a function in a programming language. `render_field` takes a form field, which is one of the class attributes we defined in `PresentationForm`, and generates appropriate HTML. The expression `field(**kwargs)|safe` generates the HTML of the input field (e.g., `<input>`,etc.), which is why we marked it `safe`. `**kwargs` means to pass any keyword arguments that were passed to `render_field` directly to the `field` object. Finally, calling the `field` object generates the appropriate HTML. Now you may be wondering, how can you call an object? Python supports the notion of _functors_: objects that can be called directly. Here's one example:
```python
>>> class foo:
>>>    def __call__(self):
>>>        print("hello")
>>> a = foo()
>>> a()
hello
```
* We've replaced the hard-coded fields HTML in the `content` block with calls to the `render_field` macro for each field in our form.
* The expression `{{ form.cssrf_token }}` generates a hidden input field which contains a token generated by the server. Here's what it generated when I visited the page:
```html
<input id="csrf_token" name="csrf_token" type="hidden" value="ImU1NTUwMTM4MzU0ZWNiYTgwNzY3NTBlNDAyOTY5N2YwYjZiYzQ2OGYi.XGkt8A.rrEhNqS7f_asvsBzNADLJQaulZU">
```
* CSRF stands for Cross-Site-Request-Forgery and it is a security vulnerability that allows a malicious attacker to masquerade as a legitimate user. Briefly, a user logins into your site and recieves an encrypted cookie with a session ID. The user is then lured into the attacker's site, where it contains Javascript that executes an AJAX request to your website. Unfortunatly, the user's browser will send the cookie along with the AJAX request so your website has no idea that the AJAX request was not made on behalf of the user. 
* The CSRF token is one mitigation strategy: the server generates a random token, hashes it, and stores it in the user's session (cookie). When recieving a request, the server hashes the token in the request and compares the hash with the value stored in the session. If the two values don't match, the request is rejected. This is why we need to generate a CSRF hidden field: so that the server can be sure that the request is valid. Note that this whole scheme depends on good encryption and on the browser not having access to the cookie.
* By default `Flask-WTF` demands that a CSRF token is included with any form.

5. Phew! those were quite a few digressions, but it is important to understand what the code does. Try to create a new presentation and make sure the validation still works.

# Edit and Delete Operations

Users many need to edit a presentation's details after it's been added due to rescheduling, incorrect details, etc. The edit view will be very similar to the add view, except that it uses prepopulated fields from the database. So let's first refactor the templates so we don't have to repeat ourselves.

> **Refactoring** refers to improving code structure without changing function.

1. Create a template `_presentation_form.html` with the following content:
```html
{% macro render_field(field) %}
  <dt>{{ field.label }}</dt>
  <dd>{{ field(**kwargs)|safe }}
  {% if field.errors %}
    <ul class="form-errors">
    {% for error in field.errors %}
      <li>{{ error }}</li>
    {% endfor %}
    </ul>
  {% endif %}
  </dd>
{% endmacro %}

<dl>
    {{ render_field(form.title) }}
    {{ render_field(form.presenters) }}
    {{ render_field(form.scheduled) }}
    {{ render_field(form.time_range) }}
    {{ render_field(form.notes) }}
</dl>
```
2. Change `create.html`:
```html
{% extends 'base.html' %}

{% block title %}Add a Presentation{% endblock %}

{% block content %}

<form method="post">
{{ form.csrf_token }}

{% include "_presentation_form.html" %}

<p><input type="submit" value="Add"/></p>

</form>

{% endblock %}
```
* The `{% include %}` statement renders the target template within the _current_ active context and puts the result where the statement is. Since `form`  can be accessed from the current context, so can it in `_presentation_form.html`.
3. Create `edit.html`:
```html
{% extends 'base.html' %}

{% block title %}Edit Presentation{% endblock %}

{% block content %}

  <form method="post">
   {{ form.csrf_token }}
   
   {% include "_presentation_form.html" %}
   
   <p><input type="submit" value="Done">
  </form>
  
  <form action="{{ url_for('delete', pid=pid) }}" method="post">
    <input class="danger" type="submit" value="Delete" onclick="return confirm('Are you sure?');">
  </form>
{% endblock %}
```
* Not much is going here. The edit form is similar to the create form. We add another form who's target is the delete action. There is a bit of inline Javascript that confirms that the user really wants to delete the presentation when he or she clicks the delete button. 
4. Add the `edit` and `delete` view functions:
```python
@app.route('/edit/<int:pid>', methods=('GET', 'POST'))
def edit(pid):
    db = connect_db()
    presentation = db.execute("""select * from presentation p where p.id = ?""", (pid,)).fetchone()

    if presentation is None:
        abort(404)
    
    form = PresentationForm(data=presentation)
    
    if form.validate_on_submit():
        db.execute("""update presentation set title = ?, presenters = ?,
            scheduled = ?, time_range = ?, notes = ? where id=?""", 
            [getattr(form, f).data for f in 
            ('title', 'presenters', 'scheduled', 'time_range', 'notes')] + [pid])
        db.commit()
        db.close()
        
        flash('Presentation has been edited')
        return redirect(url_for('home'))
    
    db.close()
    return render_template('edit.html', form=form, pid=pid)
    
@app.route('/delete/<int:pid>', methods=('POST',))
def delete(pid):
    db = connect_db()
    db.execute("""delete from presentation where id=?""", (pid,))
    db.commit()
    db.close()
    flash('Presentation deleted.')
    return redirect(url_for('home'))
```
* the `edit` function finds the requested presentation, prepopulates the form with its data, validates the `POST` request&mdash;if applicable&mdash;and either makes the edit or displays the form. Notice how in `db.execute(...)`, we are concatenating two lists: the list of values to update and a list of one element: the presentation ID.
5. Navigate to `localhost:5000/edit/1` and try editing or deleting the presentation. Try it for other presentations as well.

Having to manually enter `create` and `edit` urls is tiresome. Let's add some friendly links:

1. modify `home.html`:
```html
{% block content %}
<p class='centered-text'>
 <a href='{{ url_for("create") }}' class='btn-txt'>Add a Presentation</a>
</p>
...
```
2. modify `details.html`:
```html
{% block content %}
<p class='centered-text'>
 <a href='{{ url_for("edit", pid=p["id"]) }}' class='btn-txt'>Edit</a>
</p>
...
```

# File Uploads

Users should be able to upload useful attachments to go with presentations: the powerpoint itself, extra notes, media, etc. It is time to add this functionality to our app. The basic file upload process over HTTP is:
1. When the user issues a `POST` request, get the list of files they want to upload.
2. For each file, generate a secure file name, so that the user cannot use malicious file names to compromise the server (e.g., `../../../file`).
3. Store the file in a designated `upload` folder on the file system.
4. Make a record in the database of the attachment

## Updating the Database

We'll store records of presentation attachments in a separate table, `attachment`.

1. Add the following to the end of `schema.sql`:
```sql
DROP TABLE IF EXISTS attachment;
CREATE TABLE attachment (
    id integer primary key autoincrement,
    presentation_id integer not null,
    filename text not null,
    foreign key (presentation_id) references presentation(id)
);
```
2. Run `python initdb.py` to reinitialize the database.

## Modifying the Create View

1. Create a folder `uploads` under  `rgs`.
2. Add the following imports and config in `rgsapp.py`:
```python
import random
import os
from werkzeug.utils import secure_filename
import string
...
app.config['uploads_path'] = './uploads/'
```
3. At the bottom, add:
```python
def generate_file_name(filename):
    prefix = randstr(8)
    filename = '%s-%s' % (prefix, secure_filename(filename))
    return filename

# from stackoverflow ...
def randstr(N):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))
```
`generate_file_name` secures the given name and attaches a random prefix to it so that files with identical names don't overwrite each other. 

4. Modify the `create` view to include the attachment handling logic:
```python
if form.validate_on_submit():
        
        # upload attachments
        attachments = []
        if 'attachments' in request.files:
           for f in request.files.getlist('attachments'):
               filename = generate_file_name(f.filename)
               f.save(os.path.join(app.config['uploads_path'], filename))
               attachments.append(filename)

        db = connect_db()
        cursor = db.cursor()
        cursor.execute("""insert into presentation(title, presenters, scheduled, time_range, notes)
            values(?, ?, ?, ?, ?)""", 
            [getattr(form, f).data for f in 
            ('title', 'presenters', 'scheduled', 'time_range', 'notes')])
        
        # need to know the newly inserted presentation id
        pid = cursor.lastrowid
        
        for a in attachments:
            cursor.execute("""insert into attachment(presentation_id, filename)
             values(?, ?)""", (pid, a))
```
* `cursor` is the object that `sqlite3` uses to execute operations on the database. The previous `db.execute()` was just a short-hand which creates a cursor on the fly and executes the query on the cursor. In this case, we need the cursor to get the last insertion ID.

4. Modify `details` so that it retrieves attachments associated with a presentation:
```python
@app.route('/presentation/<int:pid>')
def details(pid):
    
    db = connect_db()
    presentation = db.execute("""select * from presentation p where p.id = ?""", (pid,)).fetchone()

    if presentation is None:
        abort(404)
    
    attachments = db.execute("""select * from attachment a where a.presentation_id = ?""", (pid,))
    
    presentation['attachments'] = list(attachments)
    
    db.close()
    
    return render_template('details.html', p=presentation)
```

5. Add a route which let's people download attachments:
```python
from flask import Flask, render_template, abort, request, redirect, url_for, \
    flash, send_from_directory
...
@app.route('/getfile/<int:aid>', methods=('GET',))
def getfile(aid):
    db = connect_db()
    attachment = db.execute("""select * from attachment a where a.id = ?""", (aid,)).fetchone()

    if attachment is None:
        db.close()
        abort(404)
        
    return send_from_directory(app.config['uploads_path'], attachment['filename'], as_attachment=True)
```
* The last `send_from_directory` function provides a secure way to deliver an attachment to the browser. It splits the file path into a directory and a filename so that malicious users cannot specify paths like `./uploads/../secret_file`. Of course, in our case this is not much of a problem because we vet the attachment file names before they get inserted into the database.

6. Add an attachments field to `PresentationForm`:
```python
attachments = FileField('Attachments')
```
* Here the PresentationForm can be used to validate the name of the file, but we don't really care about that. We define a field so that the form can render it in the template.

7. Update the form template in `_presentation_form.html`:
```html
{{ render_field(form.attachments) }}
```
8. Change the `form` tag so that it supports file uploads in `create.html`:
```html
<form method="post" enctype="multipart/form-data">
```
9. Update `details.html` so that it lists the uploaded attachments:
```html
{% if p['attachments'] %}  
<h2>Attachments</h2>
<ul>
    {% for a in p['attachments'] %}
    <li><a href="{{ url_for('getfile', aid=a['id']) }}">{{ a['filename'] }}</a></li>
    {% endfor %}
</ul>
{% endif %}
```



10. You can now try uploading files with a new presentation and they will show up when you view the details page. 

We need to update the edit view so that it allows uploading new files and removing existing ones. There are no new concepts here, so let's quickly zip through it:

1. Add a route to delete attachments:
```python
@app.route('/delete_attachment/<int:aid>', methods=('POST',))
def delete_attachment(aid):
    db = connect_db()
    attachment = db.execute("""select * from attachment a where a.id = ?""", (aid,)).fetchone()

    if attachment is None:
        db.close()
        abort(404)
    
    path = os.path.join(app.config['uploads_path'], attachment['filename'])
    if os.path.isfile(path):
        os.remove(path)
    
    db.execute("""delete from attachment where id=?""", (aid,))
    db.commit()
    db.close()
    
    flash('Attachment %s has been removed' % attachment['filename'])    
    return redirect(url_for('edit', pid=attachment['presentation_id']))
```
2. Update the `edit` view to support uploading attachments:
```python
@app.route('/edit/<int:pid>', methods=('GET', 'POST'))
def edit(pid):
    db = connect_db()
    presentation = db.execute("""select * from presentation p where p.id = ?""", (pid,)).fetchone()

    if presentation is None:
        abort(404)
    
    attachments = list(db.execute("""select * from attachment a where a.presentation_id = ?""", (pid,)))
    
    form = PresentationForm(data=presentation)
    
    if form.validate_on_submit():
        # upload attachments
        attachments = []
        if 'attachments' in request.files:
           for f in request.files.getlist('attachments'):
               filename = generate_file_name(f.filename)
               f.save(os.path.join(app.config['uploads_path'], filename))
               attachments.append(filename)
        
        db.execute("""update presentation set title = ?, presenters = ?,
            scheduled = ?, time_range = ?, notes = ? where id=?""", 
            [getattr(form, f).data for f in 
            ('title', 'presenters', 'scheduled', 'time_range', 'notes')] + [pid])
            
        for a in attachments:
            db.execute("""insert into attachment(presentation_id, filename)
             values(?, ?)""", (pid, a))
        
        db.commit()
        db.close()
        
        flash('Presentation has been edited')
        return redirect(url_for('home'))
    
    db.close()
    return render_template('edit.html', form=form, pid=pid, attachments=attachments)
```
4. Update the `delete` view to remove attachments when presentation is deleted:
```python
@app.route('/delete/<int:pid>', methods=('POST',))
def delete(pid):
    db = connect_db()

    # remove attachments
    attachments = db.execute("""select * from attachment a where a.presentation_id = ?""", (pid,))
    for a in attachments:
        path = os.path.join(app.config['uploads_path'], a['filename'])
        if os.path.isfile(path):
            os.remove(path)
    db.execute("delete from attachment where presentation_id=?", (pid,))
    
    db.execute("""delete from presentation where id=?""", (pid,))
    
    
    db.commit()
    db.close()
    flash('Presentation deleted.')
    return redirect(url_for('home'))
```

3. Update  `edit.html` to show the list of attachments and allow users to remove them:
```html
  <form method="post" enctype="multipart/form-data">
   {{ form.csrf_token }}
   
   {% include "_presentation_form.html" %}
   
   <p><input type="submit" value="Done">
  </form>
  
  <form action="{{ url_for('delete', pid=pid) }}" method="post">
    <input class="danger" type="submit" value="Delete" onclick="return confirm('Are you sure?');">
  </form>
  
{% if attachments %}  
<h2>Attachments</h2>
<ul>
    {% for a in attachments %}
    <li>
     <a href="{{ url_for('getfile', aid=a['id']) }}">{{ a['filename'] }}</a>
     <form method="post" action="{{ url_for('delete_attachment', aid=a['id']) }}">
      <input class='danger' type='submit' value='Delete'>
     </form>
    </li>
    {% endfor %}
</ul>
{% endif %}

```
Since `delete_attachment` is an operation which changes the database, we've marked as a `POST` operation. To send requests via `POST`, we have to use an HTML form. So we create one form for which attachment.

Edit some presentations by uploading new attachments or removing existing ones.

# Authentication and Authorization

We don't want just anyone to change the presentations schedule, and we may also want to restrict access to the schedule to certain users. To do this, we need to implement _authentication_ and _authorization_ mechanisms. Authenticating a user ensures that the user is who they claim to be (e.g., user mmkhajah is really Mohammad), while authorization ensures that a user has the right to do an action (e.g, can add presentation, can view presentations, etc). Authentication is typically performed with the combination of username and password, fingerprinting, etc. Authorization can be implemented with simple _roles_: a user can have an admin role, a normal role, etc.

To implement authentication and authorization, we'll need to keep track of users in our database, so add the following to the end of `schema.sql` and rerun `python initdb.py` to reinitialize the database:
```sql
DROP TABLE IF EXISTS user;
CREATE TABLE user (
    id integer primary key autoincrement,
    username text not null,
    password_hash text not null,
    user_role text not null
);
CREATE UNIQUE INDEX username_index ON user(username);
INSERT INTO user VALUES(null, 'mmkhajah', '$pbkdf2-sha256$29000$6H0vRYiRUipljBECoFQqxQ$3jePNmElDj.xZl2aw8ktbLQ/UMQbGRmn5cG3geNkJSE', 'admin');
INSERT INTO user VALUES(null, 'user1', '$pbkdf2-sha256$29000$prSW8j4nhHDundOac04JoQ$9cbvKgz/KBvRTFpGIakfcu2mc.kRO6XSKyTlUzUZAdQ', 'user');
```
* Each user has username, role, and a hashed password. 
* **Never** store the password in your database; instead, use a hashing library to store a hashed version of the password. Good hashing algorithms generate (almost) unique strings for a given input. But the operation is destructive: it is usually not possible to recover the input text, given its' hash. Because of this, storing the hashed passwords ensures that even if the database is compromised, attackers cannot recover the original passwords.
* The insert statements for users `mmkhajah` and `user1` use the SHA256 hashed versions of the passwords `hello world` and `hello world 2`, respectively. So don't worry: these long strings are not the actual passwords!

We'll need `Flask-Login` extension which takes care of the details of managing user sessions over multiple requests, and the `passlib` library which hashes passwords securely:
```sh
$ pip install flask-login passlib
```
On windows:
```cmd
> conda install flask-login passlib
```

We are going to create a login form. But first, let's refactor the `render_field` macro so that it is available to any template which needs to render forms, not just `_presentation_form.html`. 

1. Create a file `_macros.html`:
```html
{% macro render_field(field) %}
  <dt>{{ field.label }}
  <dd>{{ field(**kwargs)|safe }}
  {% if field.errors %}
    <ul class=errors>
    {% for error in field.errors %}
      <li>{{ error }}</li>
    {% endfor %}
    </ul>
  {% endif %}
  </dd>
{% endmacro %}
```
2. Modify `_presentation_form.html` so that it includes the macro, instead of defining it:
```html
{% from "_macros.html" import render_field %}
<dl>
    {{ render_field(form.title) }}
    {{ render_field(form.presenters) }}
    {{ render_field(form.scheduled) }}
    {{ render_field(form.time_range) }}
    {{ render_field(form.notes) }}
    {{ render_field(form.attachments) }}
</dl>
```
* The template now imports the `render_field` macro using what looks like Python syntax, but remember that Jinja is NOT python. After all, you cannot import `html` files in Python!
* It is common to have a template full of macros and import what you need from it using the `import` Jinja statement.
3. Verify that the add/edit forms still work.

Let's start by adding a login page to our app:

1. Create `login.html`:
```html
{% from "_macros.html" import render_field %}

{% extends 'base.html' %}

{% block title %}{% endblock %}

{% block content %}
<div class='card'>
	<h1>Login</h1>
	<form method="post">
     {{ form.csrf_token }}
        <dl>
            {{ render_field(form.username) }}
            {{ render_field(form.password) }}
        </dl>
	<p><input type="submit" value="Login"/></p>
	</form>
</div>
{% endblock %}
```

2. Create a `LoginForm` class in `forms.py`:
```python
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[vals.DataRequired()])
    password = PasswordField('Password', validators=[vals.DataRequired()])
```

3. Create the `login` view:
```python
from forms import PresentationForm, LoginForm
...
@app.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm()
    return render_template('login.html', form=form)
```
4. Verify that the new login page works by navigating to `localhost:5000/login`. Of course, the view doesn't do anything so if you submit you'll get the same form back.

Let's recap the login logic before implementing it:
1. If the request is a `POST` and both `username` and `password` fields have been filled, retrieve the database record that corresponds to `username`.
2. If no such record exists, reject login attempt. 
3. Verify that the _hash_ of the entered password matches the one in the user's record.
4. If the two match: log the user in by storing the `username` in a cryptographyically secure cookie.
5. Otherwise, reject login attempt.

For step 3, we will use the `passlib` library and for step 4, we'll use the `Flask-Login` library. 

## `passlib` Usage
let's  see how you can use `passlib` to securely store passwords:
```python
>>> from passlib.hash import pbkdf2_sha256
>>> mypassword = 'hello world'
>>> password_hash = pbkdf2_sha256.hash(mypassword)
>>> password_hash
'$pbkdf2-sha256$29000$rxXCGOM8p3SOkVKqda51Tg$VOnUI044pEF4QWnQsUj.P/Y8ugQ/HW/9o8KcDTMOIus'
>>> pbkdf2_sha256.verify('hello world', password_hash)
True
>>> pbkdf2_sha256.verify('incorrect password', password_hash) 
False
>>> password_hash2 = pbkdf2_sha256.hash(mypassword)
>>> password_hash2
'$pbkdf2-sha256$29000$GiMkBGCMca7V.v8fQ4iREg$o4yabjaFONs0OjPiUrF54j/oGnb6UtCO4CgL5g.g9yc'
>>> password_hash2 == password_hash
False
```
* `pbkdf2_sha256` is a class that implements a SHA256 hashing algorithm.
* `pbkdf2_sha256.hash` and `pbkdf2_sha256.verify` are both static functions on the class
* `hash` takes a plain string and hashes it
* `verify` verifies that the _hash_ of a plain string (first argument) is equal to a reference hash (second argument)
* `hash` will return different outputs, even for the same input, because it generates a different random _salt_ every time. So do **NOT** compare password hashes using Python's string equality directly. Use `verify` instead.

## `Flask-Login` Usage

Flask-Login makes it easy to:

* Log users in and out
* Restrict access to views to logged in users
* Manage user sessions

The library does not care how user information is stored. In fact, if you read the library's quick start example, they load user data from a plain Python dictionary. This flexibility is desirable because the library does not impose a specific database structure on the developer.

The way the library works is as follows:

* When the user is logged in, the library stores the user's ID (usually username or email) in a signed cookie (another reason why you need to have a secret key). As stated earlier, cookies are available on the client-side, so what if an attacker simply changes the user ID in the cookie to something else? the answer is because the cookie is signed using a secret key that only the server knows, any attempt to tamper with the cookie's contents will be rejected.
* When a new request arrives, the library examines the cookie and extracts the user ID. Given this ID, the library calls a function that ***you*** define to get the user's full profile (e.g., profile photo url, website, interests, role, etc.).
* By default, cookies expire when the user closes the browser. Although this can be changed by enabling a "Remember Me" feature in Flask-Login.

At a minimum, the library requires that you define a _user loader_: a function that takes a user ID and returns a user object. This function will be called whenever a new request arrives. 

Besides defining the _user loader_, the library requires that you instantiate a `LoginManager`. This class is responsible for configuring certain aspects of the login system: which login view to redirect to if an unauthenticated user attempts to open a restricted view, the login message to show, etc. 

For our application, modify `rgsapp.py`:
```python
import flask_login
...
app.config['uploads_path'] = './uploads/'

login_manager = flask_login.LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

class User(flask_login.UserMixin):
    pass

@login_manager.user_loader
def user_loader(username):
    db = connect_db()

    user_row = db.execute("select * from user u where u.username = ?", (username,)).fetchone()
    if user_row is None:
        return
    
    user = User()
    user.id = username
    user.role = user_row['user_role']

    return user
```
Here we:
* Instantiate the `LoginManager` and configure it to redirect to `login` view that we wrote earlier.
* The `User` class will contain the information about the currently logged-in user. Flask-Login expects this class to implement methods such as `is_authenticated()` and `is_active()`. For a logged-in user, these two methods usually return True so to save effort, Flask provides a sensible base class `UserMixin`. Our `User` class inherits from `UserMixin`.
* Define the user_loader: the function takes a user name and retrieves the corresponding row in the database. It then populates a new `User` object with the information and returns it. Right now, we only need to store the ID and the user's role in the `User` instance.

Now we are ready to finish the `login` view:
```python
@app.route('/login', methods=('GET', 'POST'))
def login():

    db = connect_db()
    form = LoginForm()
    
    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data

        user_row = db.execute("select * from user u where u.username = ?", (username,)).fetchone()
        
        if user_row is not None and pbkdf2_sha256.verify(password, user_row['password_hash']):
            user = User()
            
            user.id = username
            flask_login.login_user(user)
            return redirect(url_for('home'))
        flash('Incorrect Credentials')
    
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect(url_for('login'))
```
* The code attempts to retrieve the user's row from the database.
* If such row exists, it performs a hash comparison via `passlib`
* If the hashes are equal, we log the user in by calling `flask_login.login_user()` and redirect to the `home` view
* The `logout` view just logs out the currently logged in user and redirects to the login view.

Before you try this out, there is critical issue: the `connect_db()` function. Remember, this function opens a new connection to the database. But our `user_loader` also opens a connection to the database, so we'll end up with two open connections. What we really want is:

* `connect_db()` should either open a new connection or return an existing one (this is known as lazy loading)
* The database connection should automatically be closed when the request is finished. So we don't need to do `db.close()` everywhere.

Let us make changes to `rgsapp.py` that achieve these two objectives.

1. Add `g` to the list of flask imports:
```python
from flask import Flask, render_template, abort, request, redirect, url_for, flash, send_from_directory, g
```
`g` is a simple container of global variables relevant to the _current request_. It is a good place to store things such as database connections or file handles but it gets destroyed when the request ends, so don't use it to store data between requests.

2. Change `connect_db()`:
```python
def connect_db():
    
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
    
    if 'db' not in g:
        g.db = db = sqlite3.connect(app.config['db_path'],
                         detect_types=sqlite3.PARSE_DECLTYPES)
        db.row_factory = dict_factory
    
    return g.db
```
We store the database connection in `g.db`, so we first check if `g` has an attribute called `db`. If it does, we simply return `g.db`. Otherwise, we create a new connection and store it in `g.db`.

3. Remove all calls to `db.close()` in the file (find and replace would work well here)

4. Add a function `close_db`:
```python
@app.teardown_appcontext
def close_db(error):
    # removes an attribute by name
    db = g.pop('db', None)

    if db:
        db.close()
```
We remove the attribute `db` from the object `g` by using the `pop` function, which returns the attribute that was removed or `None` if no such attribute exists. If there was an active database connection, we close it with `db.close()`. Finally, we tell Flask to call `close_db` when the request is done by decorating `close_db` with `app.teardown_appcontext`.

Moment of truth. Go to `localhost:5000/login` and enter incorrect credentials. You should see 'incorrect credentials' message at the top. Try again with correct credentials (e.g., username: user1, password: hello world 2), and you should be redirected to the home view.

Let's modify the templates so that they display the currently logged in user and a link to the logout view.

1. Modify `base.html`:
```html
{% if user.id %}
  <strong>Current User:</strong> {{ user.id }} (<a href="{{ url_for('logout') }}">Logout</a>)
{% endif %}
```
`user` will be the `User` object that `Flask-Login` stores. If the user is logged in, we display a logout link.

2. Modify the `home` view so that `user` is passed to the template:
```python
output = render_template('home.html', presentations=presentations, user=flask_login.current_user)
```

3. Refresh `localhost:5000`, you should see the ID of the currently logged in user at the top along with a logout link.

4. Click the logout link, and you should be redirected to the login page.

> **Exercise**: modify the code so that the user is passed to all templates. Can you think of a more elegant way than just passing the user argument explicitly to every `render_template` call?

## Restricting Views to Logged In Users

Our login and logout processes are working, but we are not really controlling access to our views. Flask-Login provides a decorator `@flask_login.login_required` which indicates that the view function is restricted to logged in users only.

1. Open `rgsapp.py` and add the decorator `@flask_login.login_required` to all views **except** the `login` and `logout` views.
2. Make sure you are logged out. 
3. Go to `localhost:5000`: you should be redirected to the `login` view with a message "Please log in to access this page."
4. Now log in and make sure that you can access the pages as normal.

## Authorization

We want to take this a step further and only allow _admins_ to change the presentation schedule. Remember that `flask_login.current_user` refers to the currently logged user, and that our `user_loader` stores the `role` of the user in that object. Basically, we want to restrict create/edit/delete views to users with the role of `admin`. We could, in principle, do this check in every one of those views, but that would be ugly. Lets do the Pythonic thing and use a decorator.

> **NOTE**: If the user's not logged in, `flask_login.current_user` is not `None`! Instead, it is set to an instance of `AnonymousUserMixin`. This object has `is_authenticated` and `is_active` functions, but both of them return `False`.

> ### Decorators ... Round Two
> Remember than in Python, functions are first-class objects. So just like a class, a function has attributes. For example, you can get the function's name with the `__name__` attribute: 
> ```python
> >>> def greet(name):
> >>>  return "Hello %s" % (name)
> >>> greet.__name__
> 'greet'
> ```
> This is what Flask's `route` decorator uses to create a dictionary from function names to URL patterns: it gets the function name using the `__name__` attribute of the decorated function. When you call `url_for('home')`, Flask looks up the URL pattern that corresponds to function name 'home' and uses it to generate the final URL. 
>
> But now consider what happens to `__name__` when you decorate the function:
> ```python
> def strong(func):
>  def wrapper(name):
>   return "<strong>%s</strong>" % (name)
>  return wrapper
> greet = strong(greet)
> greet.__name__
> 'wrapper'
> ```
> Ooops! since the `strong` decorator is returning the nested function named `wrapper`, this is what `__name__` of `greet` show. If you use this decorator on Flask views, you will see error messages about multiple views having the same name, or that certain names do not exist. The decorator is changing the name of the decorated function.
> To fix this, Python provides a function which retains the name of the decorated function:
> ```python
> >>> from functools import wraps
> >>> def strong(func):
> >>>  @wraps(func)
> >>>  def wrapper(name):
> >>>   return "<strong>%s</strong>" % (name)
> >>>  return wrapper
> >>> @strong
> >>> def greet(name):
> >>>  return "Hello %s" % (name)
> >>> greet('Noura')
> 'Hello Noura'
> >>> greet.__name__
> 'greet'
> ```
> The `@wraps` decorator decorates the `wrapper` function. It accepts one argument, which is the original decorated function `func`. `@wraps` sets the `__name__` attribute of the `wrapper` function to the `__name__` attribute of the original decorated function `func`. Thus, the name of the original decorated function is preserved and all is well.

We'll define a decorator that limits access to views based on the user's role. 
```python
from functools import wraps
...
def requires_role(role):
    def decorator(func):
        @functools.wraps(func)
        def f(*args, **kwargs):
            if not flask_login.current_user.is_authenticated:
                abort(401)
            
            u = flask_login.current_user
            
            # if you are an admin, you have access to anything
            # otherwise, make sure your role is the same as the
            # required role
            if  u.role != 'admin' and u.role != role:
                abort(401)
            return func(*args, **kwargs)
        return f
    return decorator

@app.route('/')
...
```
* This decorator is supposed to be applied to our view functions. Before executing each function, the decorator checks that the user is not anonymous and then ensures that they have the same role as `role`. If the user has `admin` role, they will have access to everything.
* The syntax `def f(*args, **kwargs)` defines a function that takes any number of positional arguments followed by any number of keyword arguments. Our view functions have different _signatures_: some of them take no arguments, and some take one argument. We don't want to write a wrapper for each signature. The above mentioned syntax is a convenient way to handle different signatures.
* The syntax `func(*args, **kwargs)` unpacks the position and keyword arguments and passes them to `func`.

Apply this decorator as follows:
```python
@requires_role('admin')
def create():
    ...
@requires_role('admin')
def edit():
    ...
@requires_role('admin')
def delete():
    ...
@requires_role('admin')
def delete_attachment():
    ...
```

Now login to the website as an admin `mmkhajah` and check that you can still create/edit/delete presentations. Then logout and login as a normal user and try to add a presentation. You should get an error page saying you're unauthorized.

> ### Keyword Arguments ... Round Two
> If your function signature has `*a` Python will make any positional  arguments, besides the main arguments, available inside the function as an array. For example, consider the following function which joins its' arguments with a separator:
> ```python
> >>> def joiner(sep, *a):
> >>>  return sep.join(a)
> >>> joiner(',', 'hello', 'world')
> 'hello, world'
> >>> joiner(';', 'hello', 'world')
> 'hello; world'
> ```
> Notice how all positional arguments after the main argument, `sep`, are packed into an array called `a` inside the function. Similarily, if the signature has `**a`, all keyword arguments besides the main ones will be available as a dictionary called `a`. It is customary in call positional arguments `args` and keyword arguments `kwargs`, hence the signature `*args` and `**kwargs`. 
> Now, suppose you have an array of values but you want to pass them as individual arguments to a function.
> ```python
> >>> def add(a, b, c):
> >>>  return a + b + c
> >>> myvals = [3, 4, 5]
> >>> add(myvals)
> Traceback (most recent call last):
>  File "<stdin>", line 1, in <module>
> TypeError: add() missing 2 required positional arguments: 'b' and 'c'
> >>> add(*myvals)
> 12
> >>> myvals = { 'a' : 3, 'b' : 4, 'c': 5 }
> >>> add(**myvals)
> 12
> ```
> When calling a function, `*myvals` _unpacks_ the values of the array into the arguments of the function. Similarily, `**myvals` unpacks the dictionary into keyword arguments of the function. 

# Cleaning Up

Our application code is mixing SQL database access, file system access, authentication and authorization, and presentation in one place. This is generally a bad idea because you cannot modify on aspect without affecting the other. 


## Database Access
Create `db.py` in `rgsapp` folder:
```python
#
# Database access routines
#
import sqlite3
from flask import g, current_app

PRESENTATION_COLS = ['title', 'presenters', 'scheduled', 'time_range', 'notes']
ATTACHMENT_COLS = ['presentation_id', 'filename']

def connect_db():
    """ creates a new connection to a database, if one does not
    exist already within the current request"""
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
    
    if 'db' not in g:
        g.db = db = sqlite3.connect(current_app.config['DB_PATH'],
                         detect_types=sqlite3.PARSE_DECLTYPES)
        db.row_factory = dict_factory
    
    return g.db

def close_db(error):
    """ closes the connection to the database, if one exists """
    db = g.pop('db', None)
    if db:
        db.commit() # save changes
        db.close()

def get_presentations_summary():
    presentations = connect_db().execute("select * from presentation")
    return presentations

def get_presentation(pid):
    presentation = connect_db().execute("select * from presentation p where p.id = ?", (pid,)).fetchone()
    if presentation is None:
        return None 
    
    presentation['attachments'] = get_attachments(pid)

    return presentation

def create_presentation(presentation):
    pid = _insert('presentation', presentation, PRESENTATION_COLS)
    
    for a in presentation['attachments']:
        a['presentation_id'] = pid
        _insert('attachment', a, ATTACHMENT_COLS)
    

def update_presentation(presentation):
    _update('presentation', presentation, PRESENTATION_COLS)

    # insert attachments which have no ID
    for a in presentation['attachments']:
        if 'id' not in a:
            a['presentation_id'] = presentation['id']
            _insert('attachment', a, ATTACHMENT_COLS)

def delete_presentation(pid):
    connect_db().execute("delete from attachment where presentation_id = ?", (pid,))
    connect_db().execute("delete from presentation where id = ?", (pid,))

def get_attachments(pid):
    attachments = connect_db().execute("select * from attachment a where a.presentation_id = ?", (pid,))
    return list(attachments)

def get_attachment(aid):
    attachment = connect_db().execute("select * from attachment a where a.id=?", (aid,)).fetchone()
    return attachment

def delete_attachment(aid):
    connect_db().execute("delete from attachment where id=?", (aid,))

def get_user(username):
    return connect_db().execute("select * from user u where u.username = ?", (username,)).fetchone()

def _insert(table, r, columns=None):
    """ helper function for writing insert queries """
    if not columns:
        columns = list(r.keys())
    
    columns_str = ','.join(columns)
    placeholders_str = ','.join(['?'] * len(columns))

    query = "insert into %s(%s) values(%s)" % (table, columns_str, placeholders_str)

    vals = [r[c] for c in columns]

    db = connect_db()
    cursor = db.execute(query, vals)
    
    pid = cursor.lastrowid

    return pid

def _update(table, r, columns=None):
    """ helper function for writing update queries """
    if not columns:
        columns = [c for c in list(r.keys()) if c != 'id']

    columns_str = ', '.join(['%s=?' % (c) for c in columns])

    query = "update %s set %s where id=%d" % (table, columns_str, r['id'])

    vals = [r[c] for c in columns]

    connect_db().execute(query, vals)
```
We have moved all SQL database access logic into nice small functions.  The last two functions, `_insert` and `_update`, are helper functions that automatically generate the appropriate SQL queries with placeholders.  

The power of this approach is that if we decide in the future to move to another SQL database, such as Postgres, we only need to edit or replace `db.py`.

## Filesystem Management

Some of the code in `rgsapp.py` saves and deletes attachments. Saving attachments is duplicated between the `create` and `edit` views. While deleting attachments is duplicated between `delete` and `delete_attachment` views. We'll create a class that abstracts those details away.

Create `uploads_manager.py` in `rgsapp`:
```python
import os
from werkzeug.utils import secure_filename
from flask import request
import random
import string

class UploadsManager:

    def __init__(self, path, field_name):
        self.path = path
        self.field_name = field_name

    def save(self):
        filenames = []
        if self.field_name in request.files:
           for f in request.files.getlist(self.field_name):
                filename = generate_file_name(f.filename)
                f.save(os.path.join(self.path, filename))
                filenames.append(filename)
        return filenames

    def delete(self, attachment):
        path = os.path.join(self.path, attachment['filename'])
        if os.path.isfile(path):
            os.remove(path)
    
    def delete_all(self, attachments):
        for attachment in attachments:
            self.delete(attachment)

def generate_file_name(filename):
    prefix = randstr(8)
    filename = '%s-%s' % (prefix, secure_filename(filename))
    return filename

# from stackoverflow ...
def randstr(N):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))
```
This file defines a single class which handles saving and deleting attachments on the file system. The class has three methods: `save` saves all the attachments in the current request to the file system, `delete` removes a specific attachment from the file system, and `delete_all` is a convenience method that deletes all attachments in an array from the file system. Most of the logic has been copied from our old code in `rgsapp.py`.

## Authentication and Authorization

It would be nice if we can isolate our main application code from the specific authentication library used. Similarily to refactoring the database access code, this allows us to replace the authentication system by only changing or editing one file.

Create a file `auth.py`:
```python
import flask_login
import db
import functools
from passlib.hash import pbkdf2_sha256
from flask import abort

# just an alias ...
login_required = flask_login.login_required

# This class represents the currently logged in user
class User(flask_login.UserMixin):
    pass

def init(app, login_view):
    login_manager = flask_login.LoginManager()
    login_manager.login_view = login_view
    login_manager.user_loader(user_loader)
    login_manager.init_app(app)

def current_user():
    return flask_login.current_user

def user_loader(username):
    """ given a user name, return a User object representing
    the logged in user, or None if no such username exists. """
    user_row = db.get_user(username)
    
    if not user_row:
        return None

    user = User()
    user.id = username
    user.role = user_row['user_role']

    return user

def requires_role(role):
    """ requires that a user have a specific role to access
    the view """
    def decorator(func):
        @functools.wraps(func)
        def f(*args, **kwargs):
            if not flask_login.current_user.is_authenticated:
                abort(401)
            
            u = flask_login.current_user
            
            if  u.role != 'admin' and u.role != role:
                abort(401)
            return func(*args, **kwargs)
        return f
    return decorator

def authenticate(username, password):
    user_row = db.get_user(username)
    if user_row is None:
        return False
    return pbkdf2_sha256.verify(password, user_row['password_hash'])

def login_user(username):
    user = User()
    user.id = username
    flask_login.login_user(user)

def logout_user():
    flask_login.logout_user()
```
As far as the application is concerned, an authentication library should provide three main functions: a way to authenticate a username/password, a way to log a user in, and a way to log a user out. These functions correspond to the last three functions in the file. We also define some aliases that hide the fact that we are using `flask-login` from the calling code. Finally, our authorization decorator, `requires_role` has been copied to this new library.

## Putting it Together

Let's update `rgsapp.py` now that we have moved most of the functionality outside:
```python
from flask import Flask, abort, request, redirect, url_for, flash, \
    send_from_directory, g
import flask
from forms import PresentationForm, LoginForm
import db
import uploads_manager
import auth

app = Flask(__name__)
app.config['DB_PATH'] = 'db.sqlite'
app.config['UPLOADS_PATH'] = './uploads'
app.secret_key = b'xYFRlEs3@a'
app.teardown_appcontext(db.close_db)
auth.init(app, 'login')

uploads = uploads_manager.UploadsManager(app.config['UPLOADS_PATH'], 'attachments')

def render_template(*args, **kwargs):
    kwargs['user'] = auth.current_user()
    return flask.render_template(*args,**kwargs)

@app.route('/')
@auth.login_required
def home():
    
    presentations = db.get_presentations_summary()
    output = render_template('home.html', presentations=presentations)

    return output
    
@app.route('/presentation/<int:pid>')
@auth.login_required
def details(pid):
    presentation = db.get_presentation(pid)
    return render_template('details.html', p=presentation)
    
@app.route('/create', methods=('GET', 'POST'))
@auth.login_required
@auth.requires_role('admin')
def create():
    form = PresentationForm()
    
    if form.validate_on_submit():
        
        filenames = uploads.save()
        
        presentation = form.data
        presentation['attachments'] = [{ 'filename' : a } for a in filenames]

        db.create_presentation(presentation)

        flash('Presentation has been added')
        return redirect(url_for('home'))
    
    return render_template('create.html', form=form)
   
@app.route('/edit/<int:pid>', methods=('GET', 'POST'))
@auth.login_required
@auth.requires_role('admin')
def edit(pid):
    
    presentation = db.get_presentation(pid)

    if presentation is None:
        abort(404)
    
    form = PresentationForm(data=presentation)
    
    if form.validate_on_submit():

        # upload attachments
        filenames = uploads.save()
        
        old_attachments = presentation['attachments']

        presentation = form.data
        presentation['id'] = pid
        presentation['attachments'] = old_attachments + [
            { 'filename' : a, 'presentation_id' : pid } 
            for a in filenames
        ]
        
        db.update_presentation(presentation)

        flash('Presentation has been edited')
        return redirect(url_for('home'))
    
    return render_template('edit.html', form=form, pid=pid, 
        attachments=presentation['attachments'])
    
@app.route('/delete/<int:pid>', methods=('POST',))
@auth.login_required
@auth.requires_role('admin')
def delete(pid):

    presentation = db.get_presentation(pid)
    if not presentation:
        abort(404)

    uploads.delete_all(presentation['attachments'])
    
    db.delete_presentation(pid)

    flash('Presentation deleted.')
    return redirect(url_for('home'))
    
@app.route('/getfile/<int:aid>', methods=('GET',))
@auth.login_required
def getfile(aid):
    attachment = db.get_attachment(aid)

    if attachment is None:
        abort(404)
        
    return send_from_directory(app.config['UPLOADS_PATH'], attachment['filename'], as_attachment=True)
    
@app.route('/delete_attachment/<int:aid>', methods=('POST',))
@auth.login_required
@auth.requires_role('admin')
def delete_attachment(aid):
    
    attachment = db.get_attachment(aid)

    if attachment is None:
        abort(404)
    
    uploads.delete(attachment)

    db.delete_attachment(aid)

    flash('Attachment %s has been removed' % attachment['filename'])    
    return redirect(url_for('edit', pid=attachment['presentation_id']))
    
@app.route('/login', methods=('GET', 'POST'))
def login():

    if not auth.current_user().is_anonymous:
        return redirect(url_for('home'))

    form = LoginForm()
    
    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data

        if auth.authenticate(username, password):
            auth.login_user(username)
            return redirect(url_for('home'))

        flash('Incorrect Credentials')
    
    return render_template('login.html', form=form)
    
@app.route('/logout')
def logout():
    auth.logout_user()
    return redirect(url_for('login'))
```
* File management is now handled by `uploads` which is an instance of the `UploadManager` class. Notice how files in both `create` and `edit` views are saved with one line: `uploads.save()`.
* We want to inject the currently logged in user into the template context for all views, but we don't want to do it manually by passing `user` to each call to `render_template`. Instead, we _replace_ the `render_template` function which we import from `flask`, with a function that injects `user` into the template context. The function then calls the original `render_template`. Python's dynamic nature in action!
* Database access is now mostly reduced to one liners, which makes it clearer what each view is doing.
* We use `form.data` which returns a dictionary of field names to field values. The returned dictionary is directly interpreted as a presentation dictionary. 
* We changed configuration variable names on `app.config` to upper case letters because this is what Flask expects when loading configuration from external files, as we'll do in the next section.

Run the application to make sure everything still works.

# Configuration Handling

So far we've hardcoded our application configuration into the `rgsapp.py`. But this is not sustainable for two reasons:
* We may have multiple configuations: development, test, production. Each configuration has its own database, secret key, uploads directory, etc.
* It's a bad idea to hardcode secret keys into the application.

Edit `rgsapp.py` by removing the previous `app.config` lines and replacing them with:
```python
...
import default_settings

app = Flask(__name__)
app.config.from_object('default_settings')
app.config.from_envvar('RGS_SETTINGS', silent=True)

```
* Default configuration settings are loaded from a Python file called `default_settings.py` that resides in `rgsapp`
* The environment variable `RGS_SETTINGS` can be used to specify the path to a configuration file to override the default configuration. If no such environment variable exists, the defaults won't be overriden.
* The configuration files are normal Python scripts.

Create a new file called `default_settings.py` in `rgsapp`, which will contain default app configuration:
```python
SECRET_KEY = b'_5#y2L"F4Q8z\n\xec]/'
DB_PATH = 'db.sqlite'
UPLOADS_PATH = 'uploads'
```
Now stop and restart the server. Everything should work normally.

For the sake of illustration, let's define another configuration file, `rgs.config2`:
```python
SECRET_KEY = b'_5#y2L"7567\n\xec]/'
DB_PATH = 'db2.sqlite'
UPLOADS_PATH = 'uploads2'
```
Make sure to:
* Create a folder `uploads2` under `rgsapp`
* Create a copy of the database: `cp db.sqlite db2.sqlite`

Now:
1. Stop the flask server
2. `export RGS_SETTINGS=rgs.config2` in UNIX or `set RGS_SETTINGS=rgs.config2` on Windows
3. `flask run`
4. Play around with the app for a while
5. Terminate the server
6. `unset RGS_SETTINGS` on UNIX or `set RGS_SETTINGS=` on Windows
7. `flask run`

You will notice several things:
* If you were logged in before, you will be immediately thrown out and required to login. The two configuration files use different secret keys for signing the cookies. So the stored signature and the expected signature is no longer the same.
* Uploads are stored in either `uploads` or `uploads2`, depending on the configuration.
* Additions/edits/deletions in one config don't appear in the other, because they use different databases.

Annoyingly, Flask ignores `ENV` and `DEBUG` conifguration variables if they are specified in code or in the configuratin file. The reason they give is that it is too late to switch modes if these two variables are read from code or config files. In short, you still have to use `export FLASK_ENV=...` to switch modes between production and development.

# Deployment

Before proceeding, make sure to stop the flask server and unset the `RGS_SETTINGS` environment variable.

## Instance Folders
For deployment, it is a best to keep the configuration and  dynamic resources, such as the database and uploads, in one location. The same app code can then be used to host multiple deployments, with each deployment being located at a different folder. These dynamic app resources will then be kept out of source control.

Flask has the concept of _instance folders_ which allow the user to specify the base path under which dynamic resources will be located. By default, the instance folder for our project is `instance` under `rgs`. We are not making use of this folder yet because we are just specifying the paths to our database and upload folders relative to the application, not the instance path. Let's change that.

1. Change the `app` creation in `rgsapp.py` to:
```python
import os

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('default_settings')
app.config.from_pyfile('application.cfg', silent=True)
app.config['UPLOADS_PATH'] = os.path.join(app.instance_path, app.config['UPLOADS_PATH'])
app.config['DB_PATH'] = os.path.join(app.instance_path, app.config['DB_PATH'])
```
* The `instance_relative_config=True` argument tells Flask to load configuration files relative to the instance path.
* The code will first load the default settings as before, but then it will try to load settings from the `instance/application.cfg` python file. If no such file exists, it will not override the default settings.
* The last two lines define the upload and database path relative to the instance path (which Flask conveniently makes available at `app.instance_path`), rather than the application root. 

2. Modify `initdb.py` so that it takes an argument specifying the path to the database:
```python
import sqlite3
import sys
path = sys.argv[1]
db = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
...
```
* `sys` is a built-in Python library for interacting with the system.
* `sys.argv` is an array containing the arguments passed to the Python script. `sys.argv[0]` is the script name, and subsequent elements correspond to the arguments so `sys.argv[1]` is the first argument and so on.

3. Remove the `uploads` folder and `db.sqlite` from `rgs`
4. Under `rgs`, run `mkdir instance` then `mkdir instance/uploads` (use backslash for Windows)
5. Run `python initdb.py instance/db.sqlite` (again, backslash on Windows)
6. Run `flask run`. The app should work normally.

The application loads the default settings but then fails to load `instance/application.cfg` because no such file exists. Since both `DB_PATH` and `UPLOADS_PATH` are now relative to the instance path, the app uses the database and uploads folder that are under `instance`.

What is the big deal? after all, the instance path is still fixed at `./instance`, so how is this any different from what we had before? the answer is in the next section.

But before that, let's make one more change to `initdb.py`: we'll make the script initialize an instance directory for us. This means creating the database, creating uploads folder, and generating an app configuration which specifies a strong secret key.

```python
import sqlite3
import sys
import os

instance_path = sys.argv[1]

# 1. create directories recursively
uploads_path = os.path.join(instance_path, 'uploads')
if not os.path.exists(uploads_path):
    os.makedirs(uploads_path)

# 2. initialize database
db_path = os.path.join(instance_path, 'db.sqlite')
db = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
script = open('schema.sql', 'r').read()
db.executescript(script)
db.close()

# 3. generate strong key
secret_key = os.urandom(16)
#print(secret_key)

# 4. create basic configuration file
config_path = os.path.join(instance_path, 'application.cfg')
with open(config_path, 'w') as f:
    f.write('DB_PATH = %s\n' % repr('db.sqlite'))
    f.write('UPLOADS_PATH = %s\n' % repr('uploads'))
    f.write('SECRET_KEY = %s\n' % repr(secret_key))
```
We now have a handy script that preconfigures an instance folder for us. To try out, first remove the `instance` folder in `rgs` and then type:
```sh
python initdb.py instance
```
It should create the folder again with a database and app config. Run `flask run` and make sure everything still works.
 
## Production Web Server

The Flask documentation does not recommend using `flask run` for production as it is _"not designed to be particularly efficient, stable, or secure"_. Instead, they recommend using a production quality server such as _waitress_, which I have used and found to be easy to work with.

1. `pip install waitress` or `conda install waitress`
2. We are going to do something _big_: we'll wrap most of the code in `rgsapp.py` in a function called `create_app`. This function takes one argument: the `instance_path` which it internally passes to the `Flask` constructor. Doing this change will make it easy to start the production server.


## Reverse Proxy





