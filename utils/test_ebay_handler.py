import unittest
from unittest.mock import patch, MagicMock
import os
from .ebay_handler import EbayHandler
from ebaysdk.exception import ConnectionError

class TestEbayHandler(unittest.TestCase):
    def setUp(self):
        self.test_product = {
            'title': 'Test Produkt',
            'description': 'Dies ist ein Testprodukt zur Überprüfung der API-Funktionalität',
            'price': 9.99,
            'images': ['https://example.com/test-image.jpg'],
            'category_id': '11450'
        }

    def test_missing_required_fields(self):
        # Mock-API erstellen
        mock_api = MagicMock()
        handler = EbayHandler(api=mock_api)
        
        # Test mit fehlenden Pflichtfeldern
        incomplete_product = {
            'title': 'Test Produkt',
            'description': 'Test Beschreibung'
            # price, images und category_id fehlen
        }
        
        with self.assertRaises(ValueError) as context:
            handler.create_listing(incomplete_product)
        
        self.assertTrue('Fehlendes Pflichtfeld' in str(context.exception))

    def test_create_listing_success(self):
        # Mock-API erstellen
        mock_api = MagicMock()
        mock_api.execute.return_value.dict.return_value = {
            'Ack': 'Success',
            'ItemID': '123456789',
            'Timestamp': '2024-01-01T12:00:00.000Z'
        }

        # EbayHandler mit Mock-API erstellen
        handler = EbayHandler(api=mock_api)
        
        # Test durchführen
        response = handler.create_listing(self.test_product)

        # Überprüfungen
        self.assertIsNotNone(response)
        self.assertEqual(response['Ack'], 'Success')
        self.assertEqual(response['ItemID'], '123456789')
        print("Listing erfolgreich erstellt (simuliert):", response)

        # Überprüfen der API-Aufrufe
        mock_api.execute.assert_called_once()
        args = mock_api.execute.call_args[0]
        self.assertEqual(args[0], 'AddItem')

    def test_api_error_handling(self):
        # Mock-API erstellen
        mock_api = MagicMock()
        mock_api.execute.side_effect = ConnectionError("API-Fehler: Ungültige Kategorie")
        
        # EbayHandler mit Mock-API erstellen
        handler = EbayHandler(api=mock_api)
        
        # Test durchführen
        with self.assertRaises(Exception) as context:
            handler.create_listing(self.test_product)
        
        # Überprüfen der Fehlermeldung
        self.assertTrue('Fehler beim Erstellen des eBay Listings' in str(context.exception))
        self.assertTrue('API-Fehler: Ungültige Kategorie' in str(context.exception))
        print("API-Fehlerbehandlung erfolgreich getestet")

if __name__ == '__main__':
    unittest.main() 