import psycopg2
import csv


def calculate_sales_growth_with_query(db_params):
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    sales_growth_query = """
    WITH sales_data AS (
        SELECT 
            pn.category_id,
            c.name AS category_name,
            SUM(o.total_amount) AS total_sales,
            'Current Period' AS period
        FROM 
            public.orders o
        JOIN 
            public.product_ratings pr ON o.id = pr.order_id
        JOIN 
            public.products p ON pr.product_id = p.id
        JOIN 
            public.product_names pn ON p.name_id = pn.id
        JOIN 
            public.categories c ON pn.category_id = c.id
        WHERE 
            o.created_at BETWEEN '2024-09-14 17:52:36.368747' AND '2024-12-13 17:52:36.368747'
        GROUP BY 
            pn.category_id, c.name

        UNION ALL

        SELECT 
            pn.category_id,
            c.name AS category_name,
            SUM(o.total_amount) AS total_sales,
            'Previous Period' AS period
        FROM 
            public.orders o
        JOIN 
            public.product_ratings pr ON o.id = pr.order_id
        JOIN 
            public.products p ON pr.product_id = p.id
        JOIN 
            public.product_names pn ON p.name_id = pn.id
        JOIN 
            public.categories c ON pn.category_id = c.id
        WHERE 
            o.created_at BETWEEN '2024-06-16 17:52:36.368747' AND '2024-09-14 17:52:36.368747'
        GROUP BY 
            pn.category_id, c.name
    )

    SELECT 
        current.category_id,
        current.category_name,
        current.total_sales AS current_sales,
        previous.total_sales AS previous_sales,
        CASE 
            WHEN previous.total_sales = 0 THEN NULL
            ELSE ((current.total_sales - previous.total_sales) / previous.total_sales) * 100
        END AS sales_growth_percentage
    FROM 
        (SELECT category_id, category_name, total_sales 
         FROM sales_data 
         WHERE period = 'Current Period') AS current
    LEFT JOIN 
        (SELECT category_id, category_name, total_sales 
         FROM sales_data 
         WHERE period = 'Previous Period') AS previous
    ON current.category_id = previous.category_id
    ORDER BY 
        current.category_name;
    """

    cursor.execute(sales_growth_query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    return results


def write_results_to_csv(results, filename='sales_growth_results2.csv'):

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        writer.writerow(['Category ID', 'Category Name',
                        'Current Sales', 'Previous Sales', 'Growth Percentage'])

        for row in results:
            writer.writerow(row)


db_params = {
    'dbname': 'SQLTEST',
    'user': 'postgres',
    'password': 'Admin',
    'host': 'localhost',
    'port': '5432',
}


if __name__ == "__main__":
    results = calculate_sales_growth_with_query(db_params)
    if results:
        write_results_to_csv(results)
        print(f"Results written to 'sales_growth_results.csv'")
    else:
        print("No sales growth data found.")
