from django import template

def in_list(value, arg):
    return value in (arg or [])

register = template.Library()
register.filter(in_list)
