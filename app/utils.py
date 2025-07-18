def format_number(val):
    """
    Formate un nombre :
    - Si entier, affiche sans décimale
    - Sinon, affiche jusqu'à 2 décimales significatives (sans zéro inutile)
    """
    if isinstance(val, (int, float)):
        if float(val).is_integer():
            return str(int(val))
        else:
            return f"{val:.2f}".rstrip('0').rstrip('.')
    return str(val) 