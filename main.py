import mysql.connector
import pandas as pd
from datetime import datetime

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "1234567890",
    "database": "fashion"
}

def get_connection():
    conn = mysql.connector.connect(**DB_CONFIG)
    return conn

def initialize_database():
    try:
        temp_config = DB_CONFIG.copy()
        temp_config.pop("database")
        conn = mysql.connector.connect(**temp_config)
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS fashion")
        conn.close()
    except Exception as e:
        print(f"Note: Could not create database automatically: {e}")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS product(
            product_id VARCHAR(20) PRIMARY KEY,
            PName VARCHAR(50),
            brand VARCHAR(50),
            Product_for VARCHAR(20),
            season VARCHAR(20),
            rate INT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock(
            item_id VARCHAR(20) PRIMARY KEY,
            instock INT DEFAULT 0,
            status VARCHAR(15) DEFAULT 'Out of Stock',
            FOREIGN KEY (item_id) REFERENCES product(product_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchase(
            purchase_id VARCHAR(30) PRIMARY KEY,
            item_id VARCHAR(20),
            no_of_items INT,
            amount INT,
            purchase_date DATE,
            FOREIGN KEY (item_id) REFERENCES product(product_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales(
            sale_id VARCHAR(30) PRIMARY KEY,
            item_id VARCHAR(20),
            no_of_item_sold INT,
            sale_rate FLOAT,
            amount FLOAT,
            date_of_sale DATE,
            FOREIGN KEY (item_id) REFERENCES product(product_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

def product_exists(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM product WHERE product_id = %s", (product_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def get_product_rate(product_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT rate FROM product WHERE product_id = %s", (product_id,))
    result = cursor.fetchone()
    conn.close()
    return result['rate'] if result else None

def get_stock_quantity(product_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT instock FROM stock WHERE item_id = %s", (product_id,))
    result = cursor.fetchone()
    conn.close()
    return result['instock'] if result else 0

def add_product():
    print("\n" + "="*50)
    print("         ADD NEW PRODUCT")
    print("="*50)
    
    product_id = input("Enter Product ID: ").strip()
    if not product_id:
        print("Error: Product ID cannot be empty!")
        return
    
    if product_exists(product_id):
        print(f"Error: Product with ID '{product_id}' already exists!")
        return
    
    pname = input("Enter Product Name: ").strip()
    brand = input("Enter Brand: ").strip()
    product_for = input("Enter Product For (Men/Women/Kids/Unisex): ").strip()
    season = input("Enter Season (Summer/Winter/All Season): ").strip()
    
    try:
        rate = int(input("Enter Rate (Price): "))
        if rate < 0:
            print("Error: Rate cannot be negative!")
            return
    except ValueError:
        print("Error: Please enter a valid number for rate!")
        return
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO product (product_id, PName, brand, Product_for, season, rate)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (product_id, pname, brand, product_for, season, rate))
        
        cursor.execute('''
            INSERT INTO stock (item_id, instock, status)
            VALUES (%s, 0, 'Out of Stock')
        ''', (product_id,))
        
        conn.commit()
        print(f"\nProduct '{pname}' added successfully!")
    except Exception as e:
        conn.rollback()
        print(f"Error adding product: {e}")
    finally:
        conn.close()

def edit_product():
    print("\n" + "="*50)
    print("         EDIT PRODUCT")
    print("="*50)
    
    product_id = input("Enter Product ID to edit: ").strip()
    
    if not product_exists(product_id):
        print(f"Error: Product with ID '{product_id}' not found!")
        return
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM product WHERE product_id = %s", (product_id,))
    product = cursor.fetchone()
    
    print(f"\nCurrent Details:")
    print(f"  1. Product Name: {product['PName']}")
    print(f"  2. Brand: {product['brand']}")
    print(f"  3. Product For: {product['Product_for']}")
    print(f"  4. Season: {product['season']}")
    print(f"  5. Rate: {product['rate']}")
    
    print("\nWhat would you like to edit?")
    print("1. Product Name")
    print("2. Brand")
    print("3. Product For")
    print("4. Season")
    print("5. Rate")
    print("6. Edit All Fields")
    print("0. Cancel")
    
    choice = input("\nEnter your choice: ").strip()
    
    if choice == '0':
        conn.close()
        return
    
    cursor = conn.cursor()
    
    try:
        if choice == '1':
            new_value = input("Enter new Product Name: ").strip()
            cursor.execute("UPDATE product SET PName = %s WHERE product_id = %s", (new_value, product_id))
        elif choice == '2':
            new_value = input("Enter new Brand: ").strip()
            cursor.execute("UPDATE product SET brand = %s WHERE product_id = %s", (new_value, product_id))
        elif choice == '3':
            new_value = input("Enter new Product For: ").strip()
            cursor.execute("UPDATE product SET Product_for = %s WHERE product_id = %s", (new_value, product_id))
        elif choice == '4':
            new_value = input("Enter new Season: ").strip()
            cursor.execute("UPDATE product SET season = %s WHERE product_id = %s", (new_value, product_id))
        elif choice == '5':
            new_value = int(input("Enter new Rate: "))
            cursor.execute("UPDATE product SET rate = %s WHERE product_id = %s", (new_value, product_id))
        elif choice == '6':
            pname = input("Enter new Product Name: ").strip()
            brand = input("Enter new Brand: ").strip()
            product_for = input("Enter new Product For: ").strip()
            season = input("Enter new Season: ").strip()
            rate = int(input("Enter new Rate: "))
            cursor.execute('''
                UPDATE product 
                SET PName = %s, brand = %s, Product_for = %s, season = %s, rate = %s
                WHERE product_id = %s
            ''', (pname, brand, product_for, season, rate, product_id))
        else:
            print("Invalid choice!")
            conn.close()
            return
        
        conn.commit()
        print("\nProduct updated successfully!")
    except ValueError:
        print("Error: Please enter a valid number for rate!")
    except Exception as e:
        conn.rollback()
        print(f"Error updating product: {e}")
    finally:
        conn.close()

def delete_product():
    print("\n" + "="*50)
    print("         DELETE PRODUCT")
    print("="*50)
    
    product_id = input("Enter Product ID to delete: ").strip()
    
    if not product_exists(product_id):
        print(f"Error: Product with ID '{product_id}' not found!")
        return
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT PName FROM product WHERE product_id = %s", (product_id,))
    product = cursor.fetchone()
    
    print(f"\nWarning: This will delete product '{product['PName']}' and all related records!")
    print("This includes: Stock, Purchase history, and Sales history for this product.")
    confirm = input("Are you sure? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("Deletion cancelled.")
        conn.close()
        return
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM sales WHERE item_id = %s", (product_id,))
        cursor.execute("DELETE FROM purchase WHERE item_id = %s", (product_id,))
        cursor.execute("DELETE FROM stock WHERE item_id = %s", (product_id,))
        cursor.execute("DELETE FROM product WHERE product_id = %s", (product_id,))
        
        conn.commit()
        print(f"\nProduct '{product['PName']}' and all related records deleted successfully!")
    except Exception as e:
        conn.rollback()
        print(f"Error deleting product: {e}")
    finally:
        conn.close()

def view_products():
    print("\n" + "="*50)
    print("         VIEW PRODUCTS")
    print("="*50)
    print("Filter Options:")
    print("1. View All Products")
    print("2. Filter by Brand")
    print("3. Filter by Season")
    print("4. Filter by Category (Product For)")
    print("5. Filter by Price Range")
    print("0. Back to Main Menu")
    
    choice = input("\nEnter your choice: ").strip()
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = "SELECT * FROM product"
    params = []
    
    if choice == '0':
        conn.close()
        return
    elif choice == '1':
        pass
    elif choice == '2':
        brand = input("Enter Brand to filter: ").strip()
        query += " WHERE brand LIKE %s"
        params.append(f"%{brand}%")
    elif choice == '3':
        print("Available Seasons: Summer, Winter, All Season")
        season = input("Enter Season to filter: ").strip()
        query += " WHERE season LIKE %s"
        params.append(f"%{season}%")
    elif choice == '4':
        print("Available Categories: Men, Women, Kids, Unisex")
        category = input("Enter Category to filter: ").strip()
        query += " WHERE Product_for LIKE %s"
        params.append(f"%{category}%")
    elif choice == '5':
        try:
            min_price = int(input("Enter Minimum Price: "))
            max_price = int(input("Enter Maximum Price: "))
            query += " WHERE rate BETWEEN %s AND %s"
            params.extend([min_price, max_price])
        except ValueError:
            print("Error: Please enter valid numbers!")
            conn.close()
            return
    else:
        print("Invalid choice!")
        conn.close()
        return
    
    cursor.execute(query, params)
    products = cursor.fetchall()
    conn.close()
    
    if not products:
        print("\nNo products found matching your criteria.")
        return
    
    data = []
    for p in products:
        data.append({
            'Product ID': p['product_id'],
            'Name': p['PName'],
            'Brand': p['brand'],
            'For': p['Product_for'],
            'Season': p['season'],
            'Rate': p['rate']
        })
    
    df = pd.DataFrame(data)
    print("\n" + "="*80)
    print(df.to_string(index=False))
    print("="*80)
    print(f"Total Products: {len(products)}")

def generate_purchase_id():
    return f"PUR{datetime.now().strftime('%Y%m%d%H%M%S')}"

def record_purchase():
    print("\n" + "="*50)
    print("         RECORD PURCHASE")
    print("="*50)
    
    product_id = input("Enter Product ID: ").strip()
    
    if not product_exists(product_id):
        print(f"Error: Product with ID '{product_id}' not found!")
        return
    
    try:
        no_of_items = int(input("Enter Number of Items Purchased: "))
        if no_of_items <= 0:
            print("Error: Number of items must be positive!")
            return
    except ValueError:
        print("Error: Please enter a valid number!")
        return
    
    rate = get_product_rate(product_id)
    if rate is None:
        print("Error: Could not retrieve product rate!")
        return
    amount = rate * no_of_items
    
    print(f"\nPurchase Summary:")
    print(f"  Product Rate: {rate}")
    print(f"  Quantity: {no_of_items}")
    print(f"  Total Amount: {amount}")
    
    confirm = input("\nConfirm purchase? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Purchase cancelled.")
        return
    
    purchase_id = generate_purchase_id()
    purchase_date = datetime.now().strftime('%Y-%m-%d')
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute('''
            INSERT INTO purchase (purchase_id, item_id, no_of_items, amount, purchase_date)
            VALUES (%s, %s, %s, %s, %s)
        ''', (purchase_id, product_id, no_of_items, amount, purchase_date))
        
        cursor.execute("SELECT instock FROM stock WHERE item_id = %s", (product_id,))
        result = cursor.fetchone()
        
        if result:
            new_stock = result['instock'] + no_of_items
            status = 'In Stock' if new_stock > 0 else 'Out of Stock'
            cursor.execute('''
                UPDATE stock SET instock = %s, status = %s WHERE item_id = %s
            ''', (new_stock, status, product_id))
        else:
            cursor.execute('''
                INSERT INTO stock (item_id, instock, status)
                VALUES (%s, %s, 'In Stock')
            ''', (product_id, no_of_items))
        
        conn.commit()
        print(f"\nPurchase recorded successfully!")
        print(f"Purchase ID: {purchase_id}")
        print(f"Stock updated: +{no_of_items} items")
    except Exception as e:
        conn.rollback()
        print(f"Error recording purchase: {e}")
    finally:
        conn.close()

def view_purchase_history():
    print("\n" + "="*50)
    print("         PURCHASE HISTORY")
    print("="*50)
    print("Filter Options:")
    print("1. View All Purchases")
    print("2. Filter by Product ID")
    print("3. Filter by Date Range")
    print("0. Back to Main Menu")
    
    choice = input("\nEnter your choice: ").strip()
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = '''
        SELECT p.purchase_id, p.item_id, pr.PName, p.no_of_items, p.amount, p.purchase_date
        FROM purchase p
        LEFT JOIN product pr ON p.item_id = pr.product_id
    '''
    params = []
    
    if choice == '0':
        conn.close()
        return
    elif choice == '1':
        query += " ORDER BY p.purchase_date DESC"
    elif choice == '2':
        product_id = input("Enter Product ID: ").strip()
        query += " WHERE p.item_id = %s ORDER BY p.purchase_date DESC"
        params.append(product_id)
    elif choice == '3':
        try:
            start_date = input("Enter Start Date (YYYY-MM-DD): ").strip()
            end_date = input("Enter End Date (YYYY-MM-DD): ").strip()
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
            query += " WHERE p.purchase_date BETWEEN %s AND %s ORDER BY p.purchase_date DESC"
            params.extend([start_date, end_date])
        except ValueError:
            print("Error: Please enter dates in YYYY-MM-DD format!")
            conn.close()
            return
    else:
        print("Invalid choice!")
        conn.close()
        return
    
    cursor.execute(query, params)
    purchases = cursor.fetchall()
    conn.close()
    
    if not purchases:
        print("\nNo purchase records found.")
        return
    
    data = []
    total_amount = 0
    total_items = 0
    
    for p in purchases:
        data.append({
            'Purchase ID': p['purchase_id'],
            'Product ID': p['item_id'],
            'Product Name': p['PName'] or 'N/A',
            'Quantity': p['no_of_items'],
            'Amount': p['amount'],
            'Date': p['purchase_date']
        })
        total_amount += p['amount']
        total_items += p['no_of_items']
    
    df = pd.DataFrame(data)
    print("\n" + "="*100)
    print(df.to_string(index=False))
    print("="*100)
    print(f"Total Purchases: {len(purchases)} | Total Items: {total_items} | Total Amount: {total_amount}")

def generate_sale_id():
    return f"SALE{datetime.now().strftime('%Y%m%d%H%M%S')}"

def record_sale():
    print("\n" + "="*50)
    print("         RECORD SALE")
    print("="*50)
    
    product_id = input("Enter Product ID: ").strip()
    
    if not product_exists(product_id):
        print(f"Error: Product with ID '{product_id}' not found!")
        return
    
    current_stock = get_stock_quantity(product_id)
    print(f"Current Stock: {current_stock} items")
    
    if current_stock <= 0:
        print("Error: This product is out of stock!")
        return
    
    try:
        no_of_items = int(input("Enter Number of Items to Sell: "))
        if no_of_items <= 0:
            print("Error: Number of items must be positive!")
            return
        if no_of_items > current_stock:
            print(f"Error: Not enough stock! Only {current_stock} items available.")
            return
    except ValueError:
        print("Error: Please enter a valid number!")
        return
    
    rate = get_product_rate(product_id)
    if rate is None:
        print("Error: Could not retrieve product rate!")
        return
    
    try:
        discount = float(input("Enter Discount Percentage (0 for no discount): "))
        if discount < 0 or discount > 100:
            print("Error: Discount must be between 0 and 100!")
            return
    except ValueError:
        print("Error: Please enter a valid discount percentage!")
        return
    
    sale_rate = rate * (1 - discount / 100)
    amount = sale_rate * no_of_items
    
    print(f"\nSale Summary:")
    print(f"  Original Rate: {rate}")
    print(f"  Discount: {discount}%")
    print(f"  Sale Rate: {sale_rate:.2f}")
    print(f"  Quantity: {no_of_items}")
    print(f"  Total Amount: {amount:.2f}")
    
    confirm = input("\nConfirm sale? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Sale cancelled.")
        return
    
    sale_id = generate_sale_id()
    sale_date = datetime.now().strftime('%Y-%m-%d')
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO sales (sale_id, item_id, no_of_item_sold, sale_rate, amount, date_of_sale)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (sale_id, product_id, no_of_items, sale_rate, amount, sale_date))
        
        new_stock = current_stock - no_of_items
        status = 'In Stock' if new_stock > 0 else 'Out of Stock'
        cursor.execute('''
            UPDATE stock SET instock = %s, status = %s WHERE item_id = %s
        ''', (new_stock, status, product_id))
        
        conn.commit()
        print(f"\nSale recorded successfully!")
        print(f"Sale ID: {sale_id}")
        print(f"Stock updated: -{no_of_items} items (Remaining: {new_stock})")
    except Exception as e:
        conn.rollback()
        print(f"Error recording sale: {e}")
    finally:
        conn.close()

def view_sales_history():
    print("\n" + "="*50)
    print("         SALES HISTORY")
    print("="*50)
    print("Filter Options:")
    print("1. View All Sales")
    print("2. Filter by Product ID")
    print("3. Filter by Date Range")
    print("0. Back to Main Menu")
    
    choice = input("\nEnter your choice: ").strip()
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = '''
        SELECT s.sale_id, s.item_id, pr.PName, s.no_of_item_sold, s.sale_rate, s.amount, s.date_of_sale
        FROM sales s
        LEFT JOIN product pr ON s.item_id = pr.product_id
    '''
    params = []
    
    if choice == '0':
        conn.close()
        return
    elif choice == '1':
        query += " ORDER BY s.date_of_sale DESC"
    elif choice == '2':
        product_id = input("Enter Product ID: ").strip()
        query += " WHERE s.item_id = %s ORDER BY s.date_of_sale DESC"
        params.append(product_id)
    elif choice == '3':
        try:
            start_date = input("Enter Start Date (YYYY-MM-DD): ").strip()
            end_date = input("Enter End Date (YYYY-MM-DD): ").strip()
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
            query += " WHERE s.date_of_sale BETWEEN %s AND %s ORDER BY s.date_of_sale DESC"
            params.extend([start_date, end_date])
        except ValueError:
            print("Error: Please enter dates in YYYY-MM-DD format!")
            conn.close()
            return
    else:
        print("Invalid choice!")
        conn.close()
        return
    
    cursor.execute(query, params)
    sales = cursor.fetchall()
    conn.close()
    
    if not sales:
        print("\nNo sales records found.")
        return
    
    data = []
    total_amount = 0
    total_items = 0
    
    for s in sales:
        data.append({
            'Sale ID': s['sale_id'],
            'Product ID': s['item_id'],
            'Product Name': s['PName'] or 'N/A',
            'Quantity': s['no_of_item_sold'],
            'Sale Rate': f"{s['sale_rate']:.2f}",
            'Amount': f"{s['amount']:.2f}",
            'Date': s['date_of_sale']
        })
        total_amount += s['amount']
        total_items += s['no_of_item_sold']
    
    df = pd.DataFrame(data)
    print("\n" + "="*110)
    print(df.to_string(index=False))
    print("="*110)
    print(f"Total Sales: {len(sales)} | Total Items Sold: {total_items} | Total Revenue: {total_amount:.2f}")

def view_stock():
    print("\n" + "="*50)
    print("         STOCK STATUS")
    print("="*50)
    print("Filter Options:")
    print("1. View All Stock")
    print("2. View In-Stock Items Only")
    print("3. View Out-of-Stock Items Only")
    print("0. Back to Main Menu")
    
    choice = input("\nEnter your choice: ").strip()
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = '''
        SELECT s.item_id, p.PName, p.brand, p.Product_for, p.rate, s.instock, s.status
        FROM stock s
        LEFT JOIN product p ON s.item_id = p.product_id
    '''
    params = []
    
    if choice == '0':
        conn.close()
        return
    elif choice == '1':
        query += " ORDER BY s.status DESC, s.instock DESC"
    elif choice == '2':
        query += " WHERE s.status = 'In Stock' ORDER BY s.instock DESC"
    elif choice == '3':
        query += " WHERE s.status = 'Out of Stock'"
    else:
        print("Invalid choice!")
        conn.close()
        return
    
    cursor.execute(query, params)
    stock_items = cursor.fetchall()
    conn.close()
    
    if not stock_items:
        print("\nNo stock records found.")
        return
    
    data = []
    total_items = 0
    in_stock_count = 0
    out_of_stock_count = 0
    
    for s in stock_items:
        data.append({
            'Product ID': s['item_id'],
            'Name': s['PName'] or 'N/A',
            'Brand': s['brand'] or 'N/A',
            'For': s['Product_for'] or 'N/A',
            'Rate': s['rate'] or 0,
            'In Stock': s['instock'],
            'Status': s['status']
        })
        total_items += s['instock']
        if s['status'] == 'In Stock':
            in_stock_count += 1
        else:
            out_of_stock_count += 1
    
    df = pd.DataFrame(data)
    print("\n" + "="*100)
    print(df.to_string(index=False))
    print("="*100)
    print(f"Summary: {len(stock_items)} Products | In Stock: {in_stock_count} | Out of Stock: {out_of_stock_count} | Total Items: {total_items}")

def display_main_menu():
    print("\n" + "="*60)
    print("       FASHION STORE MANAGEMENT SYSTEM")
    print("="*60)
    print("  PRODUCT MANAGEMENT")
    print("    1. Add New Product")
    print("    2. Edit Product")
    print("    3. Delete Product")
    print("    4. View Products")
    print()
    print("  PURCHASE MANAGEMENT")
    print("    5. Record Purchase")
    print("    6. View Purchase History")
    print()
    print("  SALES MANAGEMENT")
    print("    7. Record Sale")
    print("    8. View Sales History")
    print()
    print("  STOCK MANAGEMENT")
    print("    9. View Stock Status")
    print()
    print("    0. Exit")
    print("="*60)

def main():
    print("\nInitializing Fashion Store Management System...")
    initialize_database()
    
    while True:
        display_main_menu()
        choice = input("Enter your choice (0-9): ").strip()
        
        if choice == '1':
            add_product()
        elif choice == '2':
            edit_product()
        elif choice == '3':
            delete_product()
        elif choice == '4':
            view_products()
        elif choice == '5':
            record_purchase()
        elif choice == '6':
            view_purchase_history()
        elif choice == '7':
            record_sale()
        elif choice == '8':
            view_sales_history()
        elif choice == '9':
            view_stock()
        elif choice == '0':
            print("\nThank you for using Fashion Store Management System!")
            print("Goodbye!")
            break
        else:
            print("\nInvalid choice! Please enter a number between 0-9.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
