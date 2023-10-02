from django import template
 
register = template.Library()

offensive_language = ['дикобраз', 'страус', 'выдра', 'навуходоносор']

@register.filter(name='censor')
def censor(value):
    for swear in offensive_language:
        value = value.replace(swear, '***')
    return value