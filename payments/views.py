import logging
import stripe
import json
from django.shortcuts import render, redirect
from django.db.models import Prefetch
from django.conf import settings
from decimal import Decimal
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from core.models import Report, Payment

# Configure logging
logging.basicConfig(level=logging.DEBUG)
app_logger = logging.getLogger(__name__)

def get_stripe_key(request):
    return JsonResponse({'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY})

def get_price(request, report_id):
    try:
        report = get_object_or_404(Report, id=report_id)
        return JsonResponse({"price": float(report.price)}, status=200)  
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    
# @csrf_exempt     
# def checkout_session(request):
#     if request.method == 'POST':
#         return JsonResponse({'id': 'test_session'})
#     else:
#         return JsonResponse({'error': 'Invalid request method'}, status=400)
@csrf_exempt 
def checkout_session(request):
    print("Request method:", request.method)
    print("Request path:", request.path)
    print("Request Body", request.body)

    stripe.api_key = settings.STRIPE_SECRET_KEY

    if request.method == 'POST':
        data = json.loads(request.body)
        app_logger.debug("Received data:", data)
        payment_id = data.get('uuid')
        user_email = request.user.email
        print(user_email)
        print(payment_id)

        if not payment_id:
                return JsonResponse({'error': 'Payment ID is required'}, status=400)

        payment = get_object_or_404(Payment, uuid=payment_id)
        print("Checkout session started with POST")

        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency':payment.currency.lower(),
                        'unit_amount': int(payment.amount *100),
                        'product_data': {
                            'name': 'Report Generation',
                        }
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri('/payment-success/'),
                cancel_url=request.build_absolute_uri('/payment-cancel'),
                # extracting customer email
                metadata={
                    'payment_id': str(payment.uuid),
                }
            )
            return JsonResponse({'id':checkout_session.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt 
def stripe_webhook(request):
    payload = request.body
    sig_header = request.MRTA.get('HTTP_STRIPE_SIGNATURE', '')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        app_logger.debug(f"Received event: {event}")
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        return HttpResponse(status=400)
    
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        payment_id = session['metadata']['payment_id']
        print(payment_id)

        try:
            payment = Payment.objects.get(id=payment_id)
            payment.status = 'succeeded'
            payment.save()
            print('payment succeeded')
            app_logger.debug(f"Report {payment.report.id} marked as paid.")
            

            if payment.report:
                payment.report.status = 'paid'
                payment.report.save()
                print('Report status updated to paid.')
        except Exception as e:
            app_logger.debug(f"Error processing webhook: {e}")

    return HttpResponse(status=200)

def payment_status(request, uuid):
    print("Payment ID received:", uuid)
    try:
        payment = get_object_or_404(Payment, uuid=uuid)
        if payment.status == 'succeeded':
            app_logger.debug(f"succeeded")
            return JsonResponse({'paid': payment.status == 'succeeded'})
        elif payment.status == 'pending':
             app_logger.debug(f"unpaid unpaid")
             return JsonResponse({'unpaid': payment.status == 'unpaid'})
        else:
            app_logger.debug(f"unpaid pending")
            return JsonResponse({'unpaid': payment.status =='pending'})
    except Payment.DoesNotExist:
        app_logger.debug(f"payment does not exist")
        return JsonResponse({'paid': False}, status=404)

def payment_success(request):
    return render(request, 'payments/payment_success.html')

def payment_cancel(request):
    return render(request, 'payments/payment_cancel.html')
