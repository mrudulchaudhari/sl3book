def cart_context(request):
    """
    Makes the cart contents (specifically item count) available
    to all templates.
    """
    cart = request.session.get('cart', {})
    cart_item_count = 0
    for quantity in cart.values():
        try:
           cart_item_count += int(quantity)
        except (ValueError, TypeError):
           pass

    return {
        'cart_item_count': cart_item_count
    }