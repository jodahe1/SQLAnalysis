import psycopg2
from datetime import datetime, timedelta
import csv


def calculate_sales_growth(db_params):
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    # Determine the date ranges for the last 90 days and the previous 90 days
    today = datetime.now()
    # Start of the last 90 days
    current_start_date = today - timedelta(days=90)
    current_end_date = today  # Today
    previous_start_date = current_start_date - \
        timedelta(days=90)  # Start of the previous 90 days
    previous_end_date = current_start_date  # End of the previous 90 days

    # Debugging: print the date ranges
    print(f"Current period: {current_start_date} to {current_end_date}")
    print(f"Previous period: {previous_start_date} to {previous_end_date}")

    # SQL query to fetch sales data for the last 90 days
    sales_query_current = """
    SELECT 
        c.id AS category_id, 
        c.name AS category_name, 
        SUM(o.total_amount) AS total_sales
    FROM 
        orders o
    JOIN 
        groups_carts gc ON o.groups_carts_id = gc.id
    JOIN 
        group_cart_variations gcv ON gc.id = gcv.group_cart_id
    JOIN 
        products p ON gcv.product_variation_id = p.id
    JOIN 
        product_names pn ON p.name_id = pn.id
    JOIN 
        categories c ON pn.category_id = c.id
    WHERE 
        o.created_at >= %s AND o.created_at < %s
    GROUP BY 
        c.id, c.name;
    """

    # SQL query to fetch sales data for the previous 90 days
    sales_query_previous = """
    SELECT 
        c.id AS category_id, 
        c.name AS category_name, 
        SUM(o.total_amount) AS total_sales
    FROM 
        orders o
    JOIN 
        groups_carts gc ON o.groups_carts_id = gc.id
    JOIN 
        group_cart_variations gcv ON gc.id = gcv.group_cart_id
    JOIN 
        products p ON gcv.product_variation_id = p.id
    JOIN 
        product_names pn ON p.name_id = pn.id
    JOIN 
        categories c ON pn.category_id = c.id
    WHERE 
        o.created_at >= %s AND o.created_at < %s
    GROUP BY 
        c.id, c.name;
    """

    # Execute queries
    cursor.execute(sales_query_current, (current_start_date, current_end_date))
    current_sales = cursor.fetchall()
    print(f"Current sales results: {current_sales}")  # Debugging output

    cursor.execute(sales_query_previous,
                   (previous_start_date, previous_end_date))
    previous_sales = cursor.fetchall()
    print(f"Previous sales results: {previous_sales}")  # Debugging output

    # Process results
    # {category_id: (name, total_sales)}
    current_sales_dict = {row[0]: (row[1], row[2]) for row in current_sales}
    # {category_id: (name, total_sales)}
    previous_sales_dict = {row[0]: (row[1], row[2]) for row in previous_sales}

    # Calculate growth percentage
    growth_results = []
    for category_id, (name, current_total) in current_sales_dict.items():
        previous_total = previous_sales_dict.get(category_id, (name, 0))[1]
        growth_percentage = ((current_total - previous_total) /
                             previous_total * 100) if previous_total > 0 else float('inf')
        growth_results.append(
            (name, current_total, previous_total, growth_percentage))

    # Close the database connection
    cursor.close()
    conn.close()

    return growth_results


def write_results_to_csv(results, filename='sales_growth_results.csv'):
    # Write the results to a CSV file
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(['Category Name', 'Current Sales',
                        'Previous Sales', 'Growth Percentage'])
        # Write the data
        for row in results:
            writer.writerow(row)


# Database connection parameters
db_params = {
    'dbname': 'SQLTEST',
    'user': 'postgres',
    'password': 'Admin',
    'host': 'localhost',
    'port': '5432',
}

# Example usage
if __name__ == "__main__":
    results = calculate_sales_growth(db_params)
    if results:
        write_results_to_csv(results)
        print(f"Results written to 'sales_growth_results.csv'")
    else:
        print("No sales growth data found.")
