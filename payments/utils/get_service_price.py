from core.models import PriceSetting, Payment

def get_service_price(service_type):
    try:
        price_setting = PriceSetting.objects.get(service_type=service_type)
        return price_setting.price, price_setting.currency
    except PriceSetting.DoesNotExist:
        return None, None
    
def get_payment_uuid(payment_uuid):
    try:
        payment_obj = Payment.objects.get(uuid=payment_uuid)
        return str(payment_obj.uuid)
    except Payment.DoesNotExist:
        return None
