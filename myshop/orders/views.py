#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------------------------
# Archivo: views.py
#
# Descripción:
#   En este archivo se definen las vistas para la app de órdenes.
#
#   A continuación se describen los métodos que se implementaron en este archivo:
#
#                                               Métodos:
#           +------------------------+--------------------------+-----------------------+
#           |         Nombre         |        Parámetros        |        Función        |
#           +------------------------+--------------------------+-----------------------+
#           |                        |                          |  - Verifica la infor- |
#           |                        |  - request: datos de     |    mación y crea la   |
#           |    order_create()      |    la solicitud.         |    orden de compra a  |
#           |                        |                          |    partir de los datos|
#           |                        |                          |    del cliente y del  |
#           |                        |                          |    carrito.           |
#           +------------------------+--------------------------+-----------------------+
#           |                        |                          |  - Crea y envía el    |
#           |        send()          |  - order_id: id del      |    correo electrónico |
#           |                        |    la orden creada.      |    para notificar la  |
#           |                        |                          |    compra.            |
#           +------------------------+--------------------------+-----------------------+
#           |                        |                          |  - Crea y envía el    |
#           |                        |  - request: datos locales|    correo electrónico |
#           |    sendMailCancel()    |    que son solicitados.  |    para notificar la  |
#           |                        |                          |    modificación de    |
#           |                        |                          |    una orden previa.  |
#           +------------------------+--------------------------+-----------------------+
#           |                        |                          |  - Crea la vista con  |
#           |       viewOrder()      |  - request: datos locales|    los datos de la    |
#           |                        |    que son solicitados.  |    orden previamente  |
#           |                        |                          |    realizada.         |
#           +------------------------+--------------------------+-----------------------+
#           |                        |                          |  - Elimina el producto|
#           |                        |   - id: Id del producto  |    dentro de la lista |
#           |  DeleteProductOrder()  |    que se está eliminando|    de ordenes, basado |
#           |                        |   - order_id: Id de la   |    en el id_producto  |
#           |                        |    orden que contiene el |    y orden que fue    |
#           |                        |                          |    mandado            |
#           +------------------------+--------------------------+-----------------------+
#
#--------------------------------------------------------------------------------------------------

from django.shortcuts import render
from .models import OrderItem, Order, Product
from .forms import OrderCreateForm
from django.core.mail import send_mail
from cart.cart import Cart
from django.shortcuts import get_object_or_404, redirect
from django.http import Http404, HttpResponseRedirect
from django.contrib import messages



def order_create(request):

    # Se crea el objeto Cart con la información recibida.
    cart = Cart(request)

    # Si la llamada es por método POST, es una creación de órden.
    if request.method == 'POST':

        # Se obtiene la información del formulario de la orden,
        # si la información es válida, se procede a crear la orden.
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'])
            
            # Se limpia el carrito con ayuda del método clear()
            cart.clear()
            
            # Llamada al método para enviar el email.
            send(order.id, cart)
            return render(request, 'orders/order/created.html', { 'cart': cart, 'order': order })
    else:
        form = OrderCreateForm()
    return render(request, 'orders/order/create.html', {'cart': cart,
                                                        'form': form})

def send(order_id, cart):
    # Se obtiene la información de la orden.
    order = Order.objects.get(id=order_id)

    # Se crea el subject del correo.
    subject = 'Order nr. {}'.format(order.id)

    # Se define el mensaje a enviar.
    message = 'Dear {},\n\nYou have successfully placed an order. Your order id is {}.\n\n\n'.format(order.first_name,order.id)
    message_part2 = 'Your order: \n\n'
    mesagges = []

    for item in cart:
        msg = str(item['quantity']) + 'x '+ str(item['product']) +'  $'+ str(item['total_price'])+ '\n'
        mesagges.append(msg)
    
    message_part3 = ' '.join(mesagges)
    message_part4 = '\n\n\n Total: $'+ str(cart.get_total_price())
    body = message + message_part2 + message_part3 + message_part4

    # Se envía el correo.
    send_mail(subject, body, 'miguel.angel.vp.98@gmail.com', [order.email], fail_silently=False)



def sendMailCancel(request):
    # Se obtiene la información de la orden.
    order = Order.objects.get(id=request.GET.get('orderid'))

    products = order.get_products()

    subject = 'Order nr. {} Updated'.format(order.id)

    if products:

        message = 'Dear {},\nYou have successfully updated your order {}.\n\n\n'.format(order.first_name,order.id)
        message_part2 = 'Your order: \n\n'
        messages_v2 = []

        products = order.get_products()

        for item in products:
            msg = str(item.quantity) + 'x '+ str(item.product) +'  $'+ str(item.get_cost())+ '\n'
            messages_v2.append(msg)

        message_part3 = ' '.join(messages_v2)
        message_part4 = '\n\n\n Total: $'+ str(order.get_total_cost())
        body = message + message_part2 + message_part3 + message_part4

    else:

        # Se define el mensaje a enviar.
        body = 'Dear {},\n\Your order {} has been canceled.'.format(order.first_name,order.id)

    # Se envía el correo.
    send_mail(subject, body, 'miguel.angel.vp.98@gmail.com', [order.email], fail_silently=False)

    # return render(request, 'orders/order/create.html', {'cart': products})
    
    messages.success(request, 'Your order has been updated, check your email for further information')

    return redirect('product_list')


def viewOrder(request):
    #Se obtiene la orden en base al id recibido.
    order = Order.objects.get(id = request.GET.get('orderid'))
    #Se obtiene la lista de todos los productos dentro de la orden.
    products = order.get_products()
    #Se regresa un contexto para que la página procese todos los productos.
    return render(request, 'orders/order/cancel.html', {'order': products})

def DeleteProductOrder(request, id, order_id):
    #Se obtiene el producto que se quiere eliminar en base a su id.
    product_to_remove = OrderItem.objects.filter(product=id).first()
    #Se selecciona el producto dentro de la orden
    variable = product_to_remove.id
    #Se elimina el producto
    product_to_remove.delete()
    #Nuevamente se obtiene la orden actual
    order = Order.objects.get(id = order_id)
    #Se obtienen los productos después de su eliminación
    products = order.get_products()
    #Se vuelve a cargar la lista de ordenes.
    return render(request, 'orders/order/cancel.html', {'order': products})

    

