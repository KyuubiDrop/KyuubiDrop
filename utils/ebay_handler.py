from ebaysdk.trading import Connection
from ebaysdk.exception import ConnectionError
import os

class EbayHandler:
    def __init__(self, api=None):
        if api is None:
            self.api = Connection(
                domain='api.ebay.com',
                appid=os.getenv('JenaganI-KyuubiDr-PRD-974a4bc32-54c633cd'),
                devid=os.getenv('6eb25fba-97ab-450c-8f08-ae9742f8a771'),
                certid=os.getenv('PRD-74a4bc3249db-1104-4bf3-92aa-fec7'),
                token=os.getenv('token'),
                config_file=None
            )
        else:
            self.api = api

    def create_listing(self, product_data):
        try:
            # Überprüfe erforderliche Felder
            required_fields = ['title', 'description', 'price', 'images', 'category_id']
            for field in required_fields:
                if field not in product_data:
                    raise ValueError(f"Fehlendes Pflichtfeld: {field}")

            # Bereite die Listing-Daten vor
            listing_data = {
                "Item": {
                    "Title": product_data['title'][:80],  # eBay erlaubt max. 80 Zeichen
                    "Description": product_data['description'],
                    "PrimaryCategory": {"CategoryID": product_data['category_id']},
                    "StartPrice": str(product_data['price']),  # Preis muss als String übergeben werden
                    "Currency": "EUR",
                    "Country": "DE",
                    "ListingDuration": "Days_30",
                    "PictureDetails": {"PictureURL": product_data['images'][:12]},  # Max. 12 Bilder
                    "ReturnPolicy": {
                        "ReturnsAcceptedOption": "ReturnsAccepted",
                        "RefundOption": "MoneyBack",
                        "ReturnsWithinOption": "Days_30",
                        "ShippingCostPaidByOption": "Buyer"
                    },
                    "DispatchTimeMax": 3,  # Versand innerhalb von 3 Tagen
                    "Site": "Germany",
                    "PaymentMethods": "PAYPAL",
                    "AutoPay": True,
                    "IntegratedMerchantCreditCardEnabled": True
                }
            }
            
            # Sende das Listing an eBay
            response = self.api.execute('AddItem', listing_data)
            return response.dict()
            
        except ConnectionError as e:
            raise Exception(f"Fehler beim Erstellen des eBay Listings: {str(e)}") 