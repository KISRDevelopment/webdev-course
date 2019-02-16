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

# Basic Flask App

Flask applications can be written in a single Python file. Let's work through a simple app:

1. Under the course directory, create a subdirectory called `hello-world`
2. Within the subdirectory create a new file called `hello-world.py`
3. Add the following contents the file and save it:

```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'
```
Here, we:
* import the `Flask` class into the script's namespace. If we had only written `import flask` then we'd have to write `flask.Flask` to refer to the Flask class.
* create an instance of a `Flask` application. The first argument to the `Flask` constructor is the name of the module or package where your application resides. For a single module Flask app, like this one, always use the special variable `__name__` which will contain the name of the currently executing module.
* create function called `hello_world` which takes no arguments and returns a string
* we _decorate_ the function with a Flask routing decorator which indicates which URL should trigger the decorated function. 

I'll get to what decorators are shortly, but first let's run the app:

```sh
$ export FLASK_APP=hello-world.py
$ export FLASK_ENV=development
$ flask run
```

* The `export` lines set _environment variables_. Environment variables are key/value pairs that are made available to all programs executed within the current environment.  The `PATH` variable, which is a list of places where programs can find executables, is a famous example of an environment variable. Note that environment variables are set per terminal, so if you launch another terminal, you'd have to re-set them.
* `FLASK_APP` tells flask which module to run and `FLASK_ENV` activates debugging mode, which prints helpful debugging messages in the browser window, and enables the automatic reloader, which reloads files upon any changes.
* `flask run` launches the development server.

Now open your web browser and navigate to `http://localhost:5000`. You should see a message saying "Hello, World!".

Let us add another page to the application, add the following lines to `hello-world.py`:

```python
@app.route('/another_page')
def another_page():
    return 'Another page!'
```

In your browser, navigate to `http://localhost:500/another_page`. You should see "Another page!" in the browser's window.

> Exercise: change `another_page():` to `another_page()5463456` and reload the url. See what happens.

## Decorators

Python treats functions as first-class objects: they can be passed around and stored in variables. To understand how decorators work, let us look at a few examples. 

1. create a file called `decorators.py`, we'll explore how decorators work in this file.
2. add the following lines:
```python
def greet(name):
    return "Hello %s" % name

print(greet("Noura"))
```
3. Run: `python decorators.py`, it should print `Hello Noura`

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

Let's unpack the `strong` function:

* It accepts a single argument, `func`.
* It defines a nested function, `wrapper`, which accepts a `name` argument. 
* `wrapper` assumes that the `func` argument references a callable object (a function). It calls the function referenced by `func` and wraps the result in the `<strong>` tag.
* It returns the `wrapper` function.
* The expression `strong(greet)` calls `strong`, passing the function `greet` to it. This expression returns the wrapper function, which is then assigned to the name `greet`.

When this code is re-run, the output will contain the greeting wrapped in `<strong>` tags. This is pretty powerful: the greeting function does not need to know anything about returning HTML, and the strong function does not need to know about greetings. We say that `strong` is a _decorator_.

Python provides syntactic sugar to make it easier to specify decorators on functions. The previous example would be:

```python
def strong_decorator(func):
    def wrapper(name):
        return "<strong>" + func(name) + "</strong>"
    return wrapper

@strong_decorator
def greet(name):
    return "Hello %s" % name

print(greet("Noura"))
```

As you may have guessed, it is possible to define multiple decorators on one function: 

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

You can find more about decorators in this  article: https://www.thecodeship.com/patterns/guide-to-python-function-decorators/

# Generating the List of Presentations

Our first requirement is to generate a list of scheduled presentations. 

First, we'll create some data to work with:

1. create a subdirectory called `app-templates` under the course's directory.
2. create a file called `presentations.json` which will contain the list of presentations we want to show. It is in Javascript-Object-Notation (JSON) format, which is a nice data transport format that is readable, minimal, and directly parsable by Javascript (unlike the monstrosity that is XML).
3. add the following content to the file and save:
```json
[
    {
        "id": 1,
        "notes": "",
        "presenters": "Mohammad",
        "scheduled": "2018-05-21",
        "time_range": "10-11am",
        "title": "Dynamic Key-Value Memory Networks for Knowledge Tracing",
        "attachments" : [
            {
                "id" : 1,
                "title" : "Presentation"
            }
        ]
    },
    {
        "id": 2,
        "notes": "",
        "presenters": "Dr. Ali Al-Hemoud",
        "scheduled": "2018-05-30",
        "time_range": "9:30-10am",
        "title": "Comparison of Indoor Air Quality in Schools: Urban vs. Industrial 'Oil & Gas' Zones in Kuwait",
        "attachments" : []
    },
    {
        "id": 3,
        "notes": "<a href=\"https://gist.github.com/mmkhajah/ae2b3421ec4bcb2bd3ecb9a2bf928cdb\">The problem with Figure 1</a>",
        "presenters": "Muneera & Megha",
        "scheduled": "2018-05-30",
        "time_range": "10-11am",
        "title": "Long-Term Spatiotemporal Analysis of Social Media for Device-to-Device Networks",
        "attachments" : [
            {
                "id" : 1,
                "title" : "Presentation"
            }
        ]
    }
]
```
In Javascript, arrays are defined with square brackets, e.g, `[1,2,3,"hello"]`, and dictionaries (also known lookup tables, hash tables, and objects) are defined with curly brackets, e.g., `{ "key1" : "value1", "key2" : "value2" }`. So the content we just added defines an array of 3 elements, where each element is a dictionary containing a presentation's details. 

First, let's see how Python handles JSON files:

1. in the `app-templates` directory, run `python` to launch the interpreter. Since Python is interpreted, you can type code and run it immediately.
3. enter:
```python
>>> import json
>>> f = open('presentations.json', 'r')
>>> presentations = json.load(f)
>>> len(presentations)
3
>>> presentations[0]
{'time_range': '10-11am', 'id': 1, 'presenters': 'Mohammad', 'scheduled': '2018-05-21', 'notes': '', 'title': 'Dynamic Key-Value Memory Networks for Knowledge Tracing'}
```
The `json` module has parsed the contents of the JSON file into plain Python objects that are easy to work with; `presentations` here is just an array of three dictionaries. To dump the contents of a Python object back to a string containing JSON, just do `json.dumps(obj)`. Converting an in-memory object to a string is called _serialization_ and converting a string back to an in-memory object is called _deserialization_. Note that not all Python objects can be serialized to JSON automatically. In those cases, you'd have to define special handlers, but that is beyond the scope of this section.

Back to Flask, create a file called `presentations-list.py` in the `app-templates` folder and put the following code in it:

```python
from flask import Flask
import json

app = Flask(__name__)
app.config['presentations_path'] = 'presentations.json'

@app.route('/')
def home():
    
    with open(app.config['presentations_path'], 'r') as f:
        presentations = json.load(f)
    
    output = "<ul>"
    for p in presentations:
        output += "<li>%s</li>" % (p['title'])
    output += "</ul>"
    
    return output
```

* the `config` instance member variable of the `app` object stores application configuration. Complex apps will have many variables (e.g., where the database is, security settings, etc.) and will likely load their configuration from a file on disk. In our case, we just have one variable: where to find our presentations list. It is a good idea to use configuration variables so that you don't hardcode them in main application code. Regardless of where the configuration is loaded from, the settings will be available in the `config` instance member.
* the `with` statement is a special Python construct that ensures that cleanup code is always executed, even if an exception occurs in the statement's body. Without it, you'd have to manually close the file if an error happens during the processing of JSON for example. In short, it is a good idea to use `with` for resources which need cleanup, such as file and database handles. You can read more about how `with` works [here](http://effbot.org/zone/python-with-statement.htm).
* the code loops through every presentation and generates a bulleted HTML list containing the title of the presentation.

In the `app-templates` directory, enter
```sh
$ export FLASK_APP=presentations-list.py
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
    {% for p in pres %}
     <tr>
      <td>{{ p['scheduled'] }} {{ p['time_range']  }}</td>
      <td><strong><em>{{ p['title'] }}</em></strong></td>
      <td>{{ p['presenters'] }}</td>
     </tr>
    {% endfor %}
   </tbody>
  </table>
 </body>
</html>
```

There are a few things going on here. The file is mostly just normal static HTML, but with some special "sauce" added to it:

* `{% ... %}` corresponds to Jinja statements. These are typically control structures (if/else, loops, etc.), include statements (to include one template into another), and extend statements (for template inheritance).
* `pres` is a variable that exists within the template's _context_. You control what gets passed into this context from Python. We'll get to that shortly.
* we access the attributes of each presentation `p` just like we do in Python.
* `{{ ... }}` prints the expression inside it to the output.

While some of the expressions inside `{% ... %}` and `{{ ... }}` look like Python code, they are **NOT** Python. So don't go around trying to execute arbitary code there. Complicated logic belongs to  application code, not in templates.

Now, modify `presentations-list.py`, so that it becomes:
```python
from flask import Flask, render_template
import json

app = Flask(__name__)
app.config['presentations_path'] = 'presentations.json'

@app.route('/')
def home():
    
    with open(app.config['presentations_path'], 'r') as f:
        presentations = json.load(f)
    
    return render_template('home.html', pres=presentations)
```
* The `render_template` function is imported from the `flask` module. It is used render Jijna templates.
* Remember the `pres` variable in `home.html`? we make it available in the template's context by assigning the `presentations` variable to the keyword argument `pres` of the function `render_template`.
* `render_template` accepts the template's file name as the first argument. It will look for it in the `templates` folder by default. The function returns the rendered template as a string.

If you refresh your browser, you should see the same output as before. Let's prettify the interface a bit and flex our CSS muscles. 

1. Create a directory called `static` under the `app-templates` directory, and create another directory `css` under `static`.
2. Create a file `style.css` under `css` with the following content:

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
}

th {
    background: DodgerBlue;
    color: white;
}

.centered-text {
    text-align: center;
}
```
3. Go back to the template `home.html` and add the following line to the `<head>` section:

```html
<link rel='stylesheet' href='{{ url_for("static", filename="css/style.css") }}' type="text/css">
```
We don't know what the URL of the application will be; during development it is `localhost` and during production it will be something else. The `url_for()` function, which Flask [makes available by default](http://flask.pocoo.org/docs/1.0/templating/) in the template's context, resolves this problem by  inserting the URL of the application during runtime. The function takes the name of an _endpoint_ and, in this case, the filename to generate a URL for. Endpoints are actions that the Flask app makes available; in our app, `home` is one such endpoint.  The `static` endpoint is a special handler for static files&mdash;files which are delivered as-is to the client. In this case, the filename we want to generate a URL for is the CSS stylesheet.

4. Replace the `for` loop in the template with:
```html
{% for p in presentations %}
<tr>
 <td class='centered-text'>{{ p['scheduled'] }}<br>{{ p['time_range']  }}</td>
 <td><strong>{{ p['title'] }}</strong></td>
 <td  class='centered-text'>{{ p['presenters'] }}</td>
</tr>
{% endfor %}
```

Back in the browser, hit `shift+F5` to force a hard refresh which will reload the CSS file. You should see a nicer looking list of presentations.

# Adding a Second Route: Presentation Details
Presentations may have extra pieces of information, such as notes or short abstracts, and we want to display those when users click on a presentation from the list. So let's add a page which shows presentation details:

1. Add a new template file, `details.html`, with the following content:
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
The line `{{ p['notes']|safe }}` introduces a _filter_. Filters modify the variables to the left of the pipe symbol. By default, Jijna _escapes_ all variables for security reasons; if a variable contains HTML code `<i>hello</i>`, it will be rendered as `\&lt;i\&gt;hello\&lt;/i\&gt;`. The safe filter tells Jinja not to escape the variable and put the HTML code directly into the template.

2. In `presentations-list.py`, add the view function:
```python
@app.route('/presentation/<int:pid>')
def details(pid):
    
    with open(app.config['presentations_path'], 'r') as f:
        presentations = json.load(f)
        
    # find the first presentation that matches pid, otherwise return None
    presentation = next((p for p in presentations if p['id'] == pid), None)
    
    if presentation is None:
        abort(404)
    
    return render_template('details.html', p=presentation)
```
and add the `abort` function to the list of imports at the top of the file. The function terminates request processing and returns with HTTP status 404 (not found). In real life, you'd probably want to define your own 404 template, but this is good enough for now.

Since each presentation has a different ID, we cannot use a constant route for the `details` view function. Instead, we use a _variable rule_ to match the ID in the URL to the view function. The pattern `/presentation/<int:pid>` tells the router to pass the value at the end of the URL as a keyword argument called `pid` to the `details` view function. It also instructs the router to convert the value to an `int` type. If Flask is unable to coerce the value into an `int`, it will return a 404 before ever executing the view function.

3. Navigate to `localhost:5000/presentation/3`, you should see details on Muneera & Megha's presentation. But something peculiar happens: the HTML code in `p['notes']` is being shown as text rather than a link&mdash;it is being _escaped_. By default, Jijna escapes all variables for security reasons because you don't want malicious users injecting evil HTML into your website. But, if you are confident that the source of HTML is safe, you can tell Jijna so through a _filter_:
```html
{{ p['notes'] | safe }}
```
Filters modify the variable on the left side of the pipe. They are functions that accept the variable on the left as the first argument and return a transformed version. In this case, the `safe` filter tells Jinja not to escape the HTML code in the variable. Jinja has a [bunch of other useful filters](http://jinja.pocoo.org/docs/2.10/templates/#builtin-filters). Refresh your browser page and you should see the expected link. 

Before moving on, verify that you get a 404 page when you use an incorrect id.

We need to add links from the home view to each presentation's details page. Open `home.html` and replace the line 
```html
<td><strong>{{ p['title'] }}</strong></td>
```

with
```html
<td><a href="{{ url_for('details', pid=p['id']) }}"><strong>{{ p['title'] }}</strong></a></td>
```
The `url_for` function strikes again! this time, the endpoint is the `details` function. Since the `details` function expects an argument called `pid`, we pass an argument with the same name to the `url_for` function. The cool thing is that the function will generate a URL that matches the pattern given in the route decorator of `details` view. Navigate to `localhost:5000` to see the result.

You might have noticed that `home.html` and `details.html` templates share a lot in common as both of them have nearly identical header sections. As good programmers, we strive to eliminate duplication. Fortunately, Jinja provides a mechanism called template inheritance which allows you to define a base template that "child" template can override parts of. 

1. Create a file called `base.html` in the template folder and put the following content in it:
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

3. Modify 'details.html':
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
Both templates indicate that they inherit from `base.html`. And both of them define the content of the blocks in the parent template that will be overriden. In this case, the two templates override `title` and `content` blocks.


# Our First Form: Creating a Presentation

So far, the application is merely transforming a JSON representation to an HTML one. For the app to be useful, users should be able to add, edit, and remove presentations.

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
</dl>

<p><input type="submit" value="Add"/></p>

</form>

{% endblock %}
```
The `form` tag has a `post` method because we intend to change the data on the server. There are two common methods in the HTTP protocol: `GET` and `POST`, information submitted over `GET` is directly encoded into the request URL (as query string parameters, e.g., `search?keywords=hello+world`), while data submitted over `POST` is included in the body of the HTTP request. For this reason, `GET` requests should only be used to retrieve information, while `POST` requests should be used for operations that cause side-effects.

Each form field we want to submit should have a `name` attribute so that the server can access it. Some fields have a `required` attribute which lets the browser do some basic validation checks which otherwise would need to be done in Javascript (yay!).

2. Add a new route for the creation form in `presentations-list.py`:
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
@app.route('/create', methods=('GET','POST'))
def create():
    
    if request.method == 'POST':
        with open(app.config['presentations_path'], 'r') as f:
            presentations = json.load(f) 
            
        # compute next id to use
        next_id = 1
        if len(presentations) > 0:
            next_id = presentations[-1]["id"] + 1
        
        # create new presentation record
        new_pres = {
            "id" : next_id,
            "attachments" : []
        }
        for field in ["title", "presenters", "scheduled", "time_range", "notes"]:
            new_pres[field] = request.form[field]
        
        presentations.append(new_pres)
        
        # write back to "database"
        with open(app.config['presentations_path'], 'w') as f:
            json.dump(presentations, f, indent=4)
        
        return redirect(url_for('home'))
    
    return render_template('create.html')
```
It is common practice to have a form view like `create` handle both `GET` and `POST` requests. If the request method is `POST`, we load our "database" from the JSON file, compute the next record ID to use, create a new record for the submission, and write back to the JSON file (I know, it is pretty dumb to write the whole database back on each submission, but I am putting off the inevitable&mdash;SQL databases&mdash;for instructional purposes). Finally, we issue a redirect response to the browser via the `redirect` function to redirect the user back to the home view. Make no mistake about what is happening here: you are not calling the `home` function directly; rather, Flask is telling the browser to navigate to a new URL, and it is the browser which will then make a new request to the `home` view.

What if the form is missing some fields? for example, if the field `title` does not exist in the form, then `request.form['title']` will raise an exception and Flask will return a 400 Bad Request error, which is good because missing fields may indicate that any attacker is trying to bypass the user interface and send data directly, so we don't need to show them a friendly error page.

Fill out the form and click submit, you should be redirected to the home screen and you should be able to see the new presentation's details, though the lack of confirmation is jarring: the user has no idea if the operation was successful or not and he or she would have to scan the list of presentations to confirm that the presentation has been added. 

A nice UI pattern that solves the lack of feedback is to show a _flash message_ on the home page that only appears after a successful form submission and disappears afterwards. The problem though is how to show the message: remember, Flask is redirecting the browser to the home page; so how would the `home` view know to show a confirmation message or not? the answer is with a cookie 🍪. 

Cookies are small containers (4KB max) of data that are exchanged between the browser and the server. They are sent to the server on every request and can be manipulated both on the server (Flask) and the client sides (i.e., from Javascript on the browser). So how are cookies useful for flashing messages? the idea is to set a cookie before redirecting the browser, and then to have the `home` view read it&mdash;like a boomerang cookie. So let's do it:

1. add `flash` to the list of names important from the `flask` module in `presentations-list.py`
2. add the following just before the `redirect()` function call in the `create` view:
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

If you try to create a new presentation and hit submit, you will see a `RuntimeError: The session is unavailable because no secret key was set`. Flask implements `sessions` which persist user information across requests. However, for security purposes, Flask _signs_ the cookies via secret key. Signing refers to computing a hash&mdash;the signature&mdash;of the value of the cookie, using the secret key. When the cookie is sent to the server, Flask hashes the received value and compares it against the signature. If they do not match, Flask discards the request. In short, we need to define a hard secret key for our app to use when signing cookies. Add the following to `presentations-list.py` under `app.config['presentations_path'] = 'presentations.json'`:
```python
app.secret_key = b'xYFRlEs3@a'
```
Note this is key is weak, but for demo purposes it should be fine. The `b'...'` syntax corresponds to a _byte literal_ in Python which can only contain ASCII characters. In real life, make sure that (a) the secret key is long and hard to guess, and (b) store it somewhere **outside** of source control tree (don't commit it to github).

Now, retry creating a presentation. You should be redirected to `home` view and you will see the "Presentation has been added" message. If you refresh the home page, the flashed messages disappear, which is the intended behavior.

> ## Why the hassle? 
> You may be wondering, why don't we just call the `home` function directly, rather than issue a redirect. We'd avoid dealing with sessions and cookies but consider what happens if you refresh the home page after submitting the form. The browser will prompt the user to "resend the data" because it thinks he or she are trying to refresh the form. By redirecting the browser, we are telling the client that the form submission is complete.

# Validating Inputs



TODO:
* validation and form errors
* edit/delete
* refactor db access
