import pandas as pd
import matplotlib.pyplot as plt
import psycopg2

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'SQLTEST',
    'user': 'postgres',
    'password': 'Admin'
}

# Fetch data
conn = psycopg2.connect(**DB_CONFIG)
query = """
SELECT 
    CASE 
        WHEN gd.id IS NOT NULL THEN 'Group Deals' 
        ELSE 'Individual Deals' 
    END AS deal_type,
    AVG(o.total_amount) AS average_amount
FROM 
    public.orders o
LEFT JOIN 
    public.group_deals gd ON o.groups_carts_id = gd.id
GROUP BY 
    deal_type;
"""
data = pd.read_sql(query, conn)
conn.close()

# Plotting
plt.figure(figsize=(8, 6))
plt.bar(data['deal_type'], data['average_amount'], color=['blue', 'orange'])
plt.xlabel('Deal Type')
plt.ylabel('Average Total Amount')
plt.title('Average Total Amount: Group Deals vs Individual Deals')
plt.xticks(rotation=45)
plt.grid(axis='y')
plt.tight_layout()
plt.show()


import time

start_time = time.time()

# Fetch data
conn = psycopg2.connect(**DB_CONFIG)
query = """
SELECT 
    CASE 
        WHEN gd.id IS NOT NULL THEN 'Group Deals' 
        ELSE 'Individual Deals' 
    END AS deal_type,
    AVG(o.total_amount) AS average_amount
FROM 
    public.orders o
LEFT JOIN 
    public.group_deals gd ON o.groups_carts_id = gd.id
GROUP BY 
    deal_type;
"""
data = pd.read_sql(query, conn)
conn.close()

print(f"Data fetching time: {time.time() - start_time:.2f} seconds")

# Continue with plotting...