import sqlite3

def init_db():
    conn = sqlite3.connect('kyuubi_drop.db')
    c = conn.cursor()
    
    # Lösche existierende Tabellen
    c.execute('DROP TABLE IF EXISTS orders')
    c.execute('DROP TABLE IF EXISTS products')
    
    # Erstelle products Tabelle
    c.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        amazon_price DECIMAL(10,2) NOT NULL,
        selling_price DECIMAL(10,2) NOT NULL,
        ebay_price DECIMAL(10,2),
        margin DECIMAL(10,2),
        image_url TEXT,
        amazon_url TEXT,
        is_active INTEGER DEFAULT 1,
        is_available INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Erstelle orders Tabelle
    c.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL DEFAULT 1,
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'pending',
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
    ''')
    
    # Erstelle Indizes
    c.execute('CREATE INDEX IF NOT EXISTS idx_orders_product_id ON orders(product_id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders(order_date)')
    
    conn.commit()
    conn.close()
    print('Datenbank erfolgreich initialisiert!')

if __name__ == '__main__':
    init_db() 