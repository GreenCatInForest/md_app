from core.models import PriceSetting

def get_service_price(service_type):
    try:
        price_setting = PriceSetting.objects.get(service_type=service_type)
        return price_setting.price, price_setting.currency
    except PriceSetting.DoesNotExist:
        return None, None