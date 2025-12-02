import os
import platform
import mysql.connector
import pandas as pd
import datetime

# Database Connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="fashion"
)
cursor = conn.cursor()

def add_product():
    product = {}
    product['product_id'] = input("Enter Product ID: ")
    product['name'] = input("Enter Product Name: ")
    product['brand'] = input("Enter Brand Name: ")
    product['category'] = input("Enter Category (Men/Women/Kids): ")
    product['season'] = input("Enter Season (Summer/Winter): ")
    product['rate'] = int(input("Enter Product Rate: "))

    cursor.execute(
        "INSERT INTO product (product_id, PName, brand, Product_for, season, rate) VALUES (%s, %s, %s, %s, %s, %s)",
        (product['product_id'], product['name'], product['brand'], product['category'], product['season'], product['rate'])
    )
    conn.commit()

    cursor.execute(
        "INSERT INTO stock (item_id, instock, status) VALUES (%s, %s, %s)",
        (product['product_id'], 0, "No")
    )
    conn.commit()

    print("✅ Product added successfully.\n")

def edit_product():
    pid = input("Enter Product ID to edit: ")

    cursor.execute("SELECT * FROM product WHERE product_id = %s", (pid,))
    record = cursor.fetchone()
    if record:
        print("Current Record:", record)
        field = input("Enter the field to update (PName, brand, Product_for, season, rate): ")
        new_value = input("Enter the new value: ")

        sql = f"UPDATE product SET {field} = %s WHERE product_id = %s"
        cursor.execute(sql, (new_value, pid))
        conn.commit()

        cursor.execute("SELECT * FROM product WHERE product_id = %s", (pid,))
        print("🔄 Updated Record:", cursor.fetchone())
    else:
        print("❌ Product ID not found.")

def delete_product():
    pid = input("Enter Product ID to delete: ")

    for table in ['sales', 'purchase', 'stock', 'product']:
        cursor.execute(f"DELETE FROM {table} WHERE item_id = %s", (pid,))
        conn.commit()

    print("🗑️ Product deleted from all records.\n")

def view_product():
    print("📋 View Options:")
    print("1. All Products")
    print("2. By Name")
    print("3. By Brand")
    print("4. By Category")
    print("5. By Season")
    print("6. By Product ID")

    choice = int(input("Enter choice: "))

    column_map = {
        2: "PName",
        3: "brand",
        4: "Product_for",
        5: "season",
        6: "product_id"
    }

    if choice == 1:
        cursor.execute("SELECT * FROM product")
    elif choice in column_map:
        value = input(f"Enter value for {column_map[choice]}: ")
        cursor.execute(f"SELECT * FROM product WHERE {column_map[choice]} = %s", (value,))
    else:
        print("❌ Invalid choice.")
        return

    for row in cursor.fetchall():
        print(row)

def purchase_product():
    now = datetime.datetime.now()
    purchase_id = "P" + now.strftime("%Y%m%d%H%M%S")

    item_id = input("Enter Product ID: ")
    quantity = int(input("Enter Quantity: "))

    cursor.execute("SELECT rate FROM product WHERE product_id = %s", (item_id,))
    rate_row = cursor.fetchone()
    if not rate_row:
        print("❌ Product not found.")
        return

    rate = rate_row[0]
    amount = rate * quantity
    date = now.strftime("%Y-%m-%d")

    cursor.execute(
        "INSERT INTO purchase (purchase_id, item_id, no_of_items, amount, purchase_date) VALUES (%s, %s, %s, %s, %s)",
        (purchase_id, item_id, quantity, amount, date)
    )
    conn.commit()

    cursor.execute("SELECT instock FROM stock WHERE item_id = %s", (item_id,))
    instock_row = cursor.fetchone()
    instock = (instock_row[0] if instock_row else 0) + quantity
    status = "Yes" if instock > 0 else "No"

    cursor.execute(
        "UPDATE stock SET instock = %s, status = %s WHERE item_id = %s",
        (instock, status, item_id)
    )
    conn.commit()

    print("✅ Purchase recorded.\n")

def view_purchases():
    product_name = input("Enter Product Name: ")
    cursor.execute(
        """SELECT p.product_id, p.PName, p.brand, pu.no_of_items, pu.purchase_date, pu.amount
           FROM product p JOIN purchase pu ON p.product_id = pu.item_id WHERE p.PName = %s""",
        (product_name,)
    )

    for row in cursor.fetchall():
        print(row)

def view_stock():
    product_name = input("Enter Product Name: ")
    cursor.execute(
        """SELECT p.product_id, p.PName, s.instock, s.status
           FROM product p JOIN stock s ON p.product_id = s.item_id WHERE p.PName = %s""",
        (product_name,)
    )

    for row in cursor.fetchall():
        print(row)

def sale_product():
    now = datetime.datetime.now()
    sale_id = "S" + now.strftime("%Y%m%d%H%M%S")

    item_id = input("Enter Product ID: ")
    quantity = int(input("Enter Quantity: "))

    cursor.execute("SELECT rate FROM product WHERE product_id = %s", (item_id,))
    rate_row = cursor.fetchone()
    if not rate_row:
        print("❌ Product not found.")
        return

    rate = rate_row[0]
    discount = int(input("Enter Discount (%): "))
    sale_rate = rate - (rate * discount / 100)
    amount = sale_rate * quantity
    date = now.strftime("%Y-%m-%d")

    cursor.execute(
        "INSERT INTO sales (sale_id, item_id, no_of_item_sold, sale_rate, amount, date_of_sale) VALUES (%s, %s, %s, %s, %s, %s)",
        (sale_id, item_id, quantity, sale_rate, amount, date)
    )
    conn.commit()

    cursor.execute("SELECT instock FROM stock WHERE item_id = %s", (item_id,))
    instock_row = cursor.fetchone()
    instock = (instock_row[0] if instock_row else 0) - quantity
    status = "Yes" if instock > 0 else "No"

    cursor.execute(
        "UPDATE stock SET instock = %s, status = %s WHERE item_id = %s",
        (instock, status, item_id)
    )
    conn.commit()

    print("✅ Sale recorded.\n")

def view_sales():
    product_name = input("Enter Product Name: ")
    cursor.execute(
        """SELECT p.product_id, p.PName, p.brand, s.no_of_item_sold, s.date_of_sale, s.amount
           FROM product p JOIN sales s ON p.product_id = s.item_id WHERE p.PName = %s""",
        (product_name,)
    )

    for row in cursor.fetchall():
        print(row)

def menu():
    while True:
        print("\n📌 MENU:")
        print("1. Add Product")
        print("2. Edit Product")
        print("3. Delete Product")
        print("4. View Products")
        print("5. Purchase Product")
        print("6. View Purchases")
        print("7. View Stock")
        print("8. Sale Product")
        print("9. View Sales")
        print("0. Exit")

        try:
            choice = int(input("Choose an option: "))
        except ValueError:
            print("❌ Please enter a valid number.")
            continue

        if choice == 1:
            add_product()
        elif choice == 2:
            edit_product()
        elif choice == 3:
            delete_product()
        elif choice == 4:
            view_product()
        elif choice == 5:
            purchase_product()
        elif choice == 6:
            view_purchases()
        elif choice == 7:
            view_stock()
        elif choice == 8:
            sale_product()
        elif choice == 9:
            view_sales()
        elif choice == 0:
            print("👋 Exiting...")
            break
        else:
            print("❌ Invalid option.")

# Welcome Banner
print("*" * 80)
print("*" * 20 + " Welcome to the Central Fashion Store " + "*" * 20)
print("*" * 26 + " Created by: Saaim Hayat " + "*" * 27)
print("*" * 80)

menu()
