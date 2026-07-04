import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

STATUS_EMAIL_CONFIG = {
    'Shipped': {
        'subject': 'Order #{order_id} Shipped - PickUp',
        'header_title': 'PickUp Store',
        'header_subtitle': 'Order Shipped Successfully',
        'status_message': (
            'Great news! Your order has been shipped and is on its way. '
            'You can track your shipment using the tracking number below. '
            'Thank you for shopping with PickUp.'
        ),
        'status_box_style': 'background-color: #e7f2ff; border-left: 4px solid #0d6efd; color: #0b63d6;',
        'status_note': 'We are excited to let you know your order is now en route.',
    },
    'Delivered': {
        'subject': 'Order #{order_id} Delivered - PickUp',
        'header_title': 'PickUp Store',
        'header_subtitle': 'Order Delivered Successfully',
        'status_message': (
            'Your order has been delivered! We hope you enjoy your purchase. '
            'If you have any questions or need assistance, our support team is here to help.'
        ),
        'status_box_style': 'background-color: #ebffeb; border-left: 4px solid #28a745; color: #155724;',
        'status_note': 'Thank you for shopping with PickUp. We hope you love your order!',
    },
    'Cancelled': {
        'subject': 'Order #{order_id} Cancelled - PickUp',
        'header_title': 'PickUp Store',
        'header_subtitle': 'Order Cancelled',
        'status_message': (
            'Your order has been cancelled. If you believe this was an error or would like assistance, '
            'please contact our support team and we will help resolve it.'
        ),
        'status_box_style': 'background-color: #fff1f0; border-left: 4px solid #dc3545; color: #842029;',
        'status_note': 'If a refund is due, it will be processed within 3-5 business days.',
    },
}


def _build_receipt_text(order, status=None, payment_id=None):
    order_status = status or order.status
    lines = [
        '==================================================',
        '                 PICKUP ORDER RECEIPT',
        '==================================================',
        f'Order ID:        #{order.id}',
    ]
    if payment_id:
        lines.append(f'Transaction ID:  {payment_id}')
    lines.extend([
        f'Order Status:    {order_status}',
        f'Order Date:      {order.created_at.strftime("%B %d, %Y, %I:%M %p")}',
        '',
        'Customer Details:',
        '-----------------',
        f'Name:            {order.name}',
        f'Email:           {order.email}',
        f'Phone:           {order.phone}',
        '',
        'Shipping Address:',
        '-----------------',
        order.address,
        f'{order.city}, {order.state} - {order.pincode}',
        '',
        'Items Purchased:',
        '----------------',
    ])

    for item in order.items.all():
        lines.append(
            f'- {item.product.name[:30]:30} Qty: {item.quantity:<4} Price: ₹{item.price:<8} Subtotal: ₹{item.get_subtotal()}'
        )

    lines.extend([
        '',
        'Pricing Summary:',
        '----------------',
        f'Total Amount:    ₹{order.total_price}',
        '',
        '==================================================',
        'Thank you for shopping with PickUp Store!',
        '==================================================',
    ])

    return '\n'.join(lines)


def send_order_success_email(order, payment_id):
    subject = f'Order #{order.id} Placed Successfully - PickUp'
    try:
        html_content = render_to_string('emails/payment_success.html', {
            'order': order,
            'payment_id': payment_id,
        })
    except Exception as exc:
        logger.exception('Failed to render payment success email template: %s', exc)
        html_content = (
            f'Thank you for your payment! Your order #{order.id} has been placed. '
            f'Payment ID: {payment_id}.'
        )

    email = EmailMessage(
        subject=subject,
        body=html_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[order.email],
    )
    email.content_subtype = 'html'
    receipt_text = _build_receipt_text(order, status='Confirmed', payment_id=payment_id)
    email.attach(f'receipt_order_{order.id}.txt', receipt_text, 'text/plain')

    try:
        email.send(fail_silently=False)
    except Exception as exc:
        logger.exception('Failed to send order success email for order %s: %s', order.id, exc)


def send_order_status_email(order, status, previous_status=None):
    config = STATUS_EMAIL_CONFIG.get(status)
    if not config:
        return

    subject = config['subject'].format(order_id=order.id)
    try:
        html_content = render_to_string('emails/order_status_update.html', {
            'order': order,
            'status': status,
            'previous_status': previous_status,
            'header_title': config['header_title'],
            'header_subtitle': config['header_subtitle'],
            'status_message': config['status_message'],
            'status_note': config['status_note'],
            'status_box_style': config['status_box_style'],
        })
    except Exception as exc:
        logger.exception('Failed to render status update email template: %s', exc)
        html_content = (
            f'Your order #{order.id} status has been updated to {status}. '
            f'Please visit your PickUp account for details.'
        )

    email = EmailMessage(
        subject=subject,
        body=html_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[order.email],
    )
    email.content_subtype = 'html'
    receipt_text = _build_receipt_text(order, status=status)
    email.attach(f'order_status_update_{order.id}.txt', receipt_text, 'text/plain')

    try:
        email.send(fail_silently=False)
    except Exception as exc:
        logger.exception('Failed to send order status email for order %s: %s', order.id, exc)
