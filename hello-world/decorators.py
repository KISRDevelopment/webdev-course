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