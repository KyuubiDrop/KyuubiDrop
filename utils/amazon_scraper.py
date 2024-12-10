import requests
from bs4 import BeautifulSoup
import re
import time

class AmazonScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'de,en-US;q=0.7,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    def get_product_data(self, url):
        try:
            # Füge einen kleinen Delay hinzu
            time.sleep(2)
            
            # Debug-Ausgabe
            print(f"Versuche URL zu laden: {url}")
            
            response = requests.get(url, headers=self.headers, timeout=10)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extrahiere Daten
                title = self._get_title(soup)
                print(f"Gefundener Titel: {title}")
                
                amazon_price = self._get_price(soup)
                print(f"Gefundener Preis: {amazon_price}")
                
                description = self._get_description(soup)
                print(f"Beschreibung gefunden: {len(description) > 0}")
                
                image_url = self._get_image(soup)
                print(f"Bild-URL gefunden: {image_url != ''}")
                
                if not title or amazon_price == 0.0:
                    raise Exception("Wesentliche Produktdaten konnten nicht extrahiert werden")
                
                return {
                    'title': title,
                    'amazon_price': amazon_price,
                    'description': description,
                    'image_url': image_url,
                    'margin': 30.0,
                    'ebay_price': self._calculate_ebay_price(amazon_price, 30.0),
                    'source_url': url,
                    'images': [image_url] if image_url else []  # Für Kompatibilität mit dem bestehenden Code
                }
            else:
                raise Exception(f"HTTP Status Code: {response.status_code}")
                
        except Exception as e:
            print(f"Debug - Detaillierter Fehler: {str(e)}")
            raise Exception(f"Fehler beim Scrapen: {str(e)}")

    def _get_title(self, soup):
        selectors = [
            ('span', {'id': 'productTitle'}),
            ('h1', {'id': 'title'}),
            ('h1', {'class': 'product-title-word-break'})
        ]
        
        for tag, attrs in selectors:
            element = soup.find(tag, attrs)
            if element:
                title = element.get_text(strip=True)
                if title:
                    return title
                    
        return None

    def _get_price(self, soup):
        price_text = None
        
        # Neue Preisselektoren
        selectors = [
            ('span', {'class': 'a-price-whole'}),
            ('span', {'class': 'a-offscreen'}),
            ('span', {'id': 'priceblock_ourprice'}),
            ('span', {'id': 'priceblock_dealprice'}),
            ('span', {'class': 'a-price'})
        ]
        
        for tag, attrs in selectors:
            element = soup.find(tag, attrs)
            if element:
                price_text = element.get_text(strip=True)
                break
        
        if price_text:
            # Entferne alle nicht-numerischen Zeichen außer Punkt und Komma
            price_text = re.sub(r'[^0-9,.]', '', price_text)
            # Ersetze Komma durch Punkt
            price_text = price_text.replace(',', '.')
            # Finde die erste gültige Zahl
            match = re.search(r'\d+\.?\d*', price_text)
            if match:
                return float(match.group())
        
        return 0.0

    def _get_description(self, soup):
        try:
            description_parts = []
            print("Starte Beschreibungsextraktion...")

            # 1. Feature Bullets (meist die wichtigsten Produktmerkmale)
            feature_div = soup.find('div', {'id': ['feature-bullets', 'featurebullets_feature_div']})
            if feature_div:
                print("Feature Bullets gefunden")
                bullets = feature_div.find_all('span', {'class': 'a-list-item'})
                for bullet in bullets:
                    text = bullet.get_text(strip=True)
                    if text and len(text) > 5:  # Ignoriere zu kurze Einträge
                        description_parts.append(f"• {text}")

            # 2. Produktbeschreibung
            description_div = soup.find('div', {'id': 'productDescription'})
            if description_div:
                print("Produktbeschreibung gefunden")
                desc_text = description_div.get_text(strip=True)
                if desc_text:
                    description_parts.append("\nProduktbeschreibung:")
                    description_parts.append(desc_text)

            # 3. Produktdetails
            detail_bullets = soup.find('div', {'id': 'detailBullets_feature_div'})
            if detail_bullets:
                print("Produktdetails gefunden")
                details = detail_bullets.find_all('span', {'class': 'a-list-item'})
                if details:
                    description_parts.append("\nProduktdetails:")
                    for detail in details:
                        text = detail.get_text(strip=True)
                        if ':' in text:
                            # Bereinige die Detail-Texte
                            text = text.replace('\u200e', '').replace('\u200f', '')
                            description_parts.append(f"• {text}")

            # 4. Alternative: Produktübersicht
            if not description_parts:
                print("Suche in alternativer Produktübersicht...")
                overview = soup.find('div', {'id': ['productOverview_feature_div', 'dpx-product-description_feature_div']})
                if overview:
                    rows = overview.find_all(['tr', 'div'], {'class': ['a-spacing-small', 'a-row']})
                    for row in rows:
                        label = row.find(['th', 'span'], {'class': ['a-text-left', 'a-text-bold']})
                        value = row.find(['td', 'span'], {'class': ['a-text-left', 'a-text-normal']})
                        if label and value:
                            description_parts.append(f"• {label.get_text(strip=True)}: {value.get_text(strip=True)}")

            # Zusammenführen und Formatieren der Beschreibung
            if description_parts:
                print(f"Anzahl gefundener Beschreibungsteile: {len(description_parts)}")
                final_description = "\n".join(description_parts)
                
                # Bereinigung
                final_description = re.sub(r'\s+', ' ', final_description)  # Entferne mehrfache Leerzeichen
                final_description = re.sub(r'\n\s*\n', '\n\n', final_description)  # Normalisiere Absätze
                final_description = final_description.strip()
                
                print("Beschreibung erfolgreich erstellt")
                return final_description
            else:
                print("Keine Beschreibungselemente gefunden")
                return "Keine Beschreibung verfügbar"

        except Exception as e:
            print(f"Fehler bei der Beschreibungsextraktion: {str(e)}")
            return "Fehler beim Laden der Beschreibung"

    def _get_image(self, soup):
        # Versuche das Hauptbild zu finden
        for img in soup.find_all('img'):
            if any(key in img.get('id', '') for key in ['landingImage', 'imgBlkFront', 'main-image']):
                for attr in ['src', 'data-old-hires', 'data-a-dynamic-image']:
                    url = img.get(attr)
                    if url and 'data:image' not in url:
                        return url
        return ''

    def _calculate_ebay_price(self, amazon_price, margin_percentage):
        try:
            margin_multiplier = 1 + (margin_percentage / 100)
            return round(amazon_price * margin_multiplier, 2)
        except:
            return 0.0