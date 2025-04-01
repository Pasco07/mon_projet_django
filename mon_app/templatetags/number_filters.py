from django import template

register = template.Library()

@register.filter(name='format_fr')
def format_fr(value):
    """
    Formatte les nombres à la française : 
    - espace comme séparateur de milliers
    - virgule comme séparateur décimal
    """
    try:
        if value in ('-', '', None):
            return value
            
        num = float(value)
        return f"{num:,.2f}".replace(",", "X").replace(".", ",").replace("X", " ")
    except (ValueError, TypeError):
        return str(value)