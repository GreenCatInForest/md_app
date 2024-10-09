import stripe
import logging
import json

from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from core.models import Report, Payment


# Activate Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

# Configure logging for debugging
app_logger = logging.getLogger(__name__)

@login_required
def create_checkout_session(request, payment_id):

    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    report = payment.report

    if payment.payment_status == 'paid':
        # Payment already completed
        return redirect('payments:payment-success')
    
    domain_url = request.build_absolute_uri('/')[:-1]  # Remove trailing slash
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': payment.currency,
                        'product_data': {
                            'name': f'Report Payment - Report ID {report.id}',
                        },
                        'unit_amount': int(payment.amount * 100),  # Amount in cents
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=domain_url + reverse('payments:payment-success') + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=domain_url + reverse('payments:payment-cancel'),
            metadata={
                'payment_id': payment.id,
                'report_id': report.id,
                'user_id': request.user.id,
            }
        )

        # Save the Stripe Checkout Session ID
        payment.stripe_checkout_session_id = checkout_session.id
        payment.save()

        return redirect(checkout_session.url, code=303)
    except Exception as e:
        app_logger.error(f"Error creating Stripe Checkout Session: {e}")
        return JsonResponse({'error': 'An error occurred while creating the payment session.'}, status=500)
    

def payment_success(request):
    session_id = request.GET.get('session_id', None)
    if not session_id:
        return redirect('reports:create-report')  # Adjust as per your URL names

    try:
        session = stripe.checkout.Session.retrieve(session_id)
        payment_intent = stripe.PaymentIntent.retrieve(session.payment_intent)
    except Exception as e:
        app_logger.error(f"Error retrieving Stripe session: {e}")
        return redirect('reports:create-report')

    payment_id = session.metadata.get('payment_id')
    user_id = session.metadata.get('user_id')

    payment = Payment.objects.filter(id=payment_id, user_id=user_id).first()
    if payment:
        payment.payment_status = 'paid'
        payment.save()

    # Redirect to the report PDF view or display a success message
    report = get_object_or_404(Report, id=payment.report.id)
    return render(request, 'payments/success.html', {'report': report})



def payment_cancel(request):
    # Handle payment cancellation
    return render(request, 'payments/cancel.html')

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        # Invalid payload
        app_logger.error(f"Invalid payload: {e}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        app_logger.error(f"Invalid signature: {e}")
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_session(session)
    # ... handle other event types if necessary ...

    return HttpResponse(status=200)

def handle_checkout_session(session):
    app_logger.info(f"Handling checkout.session.completed for session ID: {session.id}")
    payment_id = session.metadata.get('payment_id')
    user_id = session.metadata.get('user_id')
    payment = Payment.objects.filter(id=payment_id, user_id=user_id).first()
    if payment:
        payment.payment_status = 'paid'
        payment.save()
        app_logger.info(f"Payment {payment.id} marked as paid.")