from django import template

register = template.Library()

@register.filter(name='short_transport_name')
def short_transport_name(value):
    transport_types = {
        'Машина': 'c',
        'Мотоцикл': 'm',
        'Самокат': 's'
    }
    return transport_types[value]