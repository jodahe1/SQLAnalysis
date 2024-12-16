WITH last_order_date AS (
    SELECT 
        MAX(created_at) AS max_date
    FROM 
        public.orders
),
order_data AS (
    SELECT 
        p.id AS product_id,
        pn.name AS product_name,
        c.name AS category_name,
        pvs.stock AS current_stock,
        pvp.price AS current_price,
        COALESCE(SUM(o.total_amount), 0) AS total_sales_last_3_months,
        COALESCE(AVG(pr.rating), 0) AS average_rating,
        COUNT(DISTINCT o.id) AS total_orders_last_3_months,
        (SELECT COUNT(*) 
         FROM public.orders o2 
         WHERE o2.created_at >= (SELECT max_date FROM last_order_date) - INTERVAL '6 months' 
         AND o2.id IN (SELECT pr2.order_id FROM public.product_ratings pr2 WHERE pr2.product_id = p.id)) AS total_orders_last_6_months,
        (SELECT COUNT(*) 
         FROM public.orders o3 
         WHERE o3.created_at >= (SELECT max_date FROM last_order_date) - INTERVAL '3 months' 
         AND o3.id IN (SELECT pr3.order_id FROM public.product_ratings pr3 WHERE pr3.product_id = p.id)) AS total_orders_last_3_months_subquery,
        pv.weight AS product_weight,
        pv.status AS variation_status
    FROM 
        public.products p
    JOIN 
        public.product_names pn ON p.name_id = pn.id
    JOIN 
        public.categories c ON pn.category_id = c.id
    JOIN 
        public.product_variations pv ON p.id = pv.product_id
    JOIN 
        public.product_variation_stocks pvs ON pv.id = pvs.product_variation_id
    LEFT JOIN 
        public.product_variation_prices pvp ON pv.id = pvp.product_variation_id
    LEFT JOIN 
        public.product_ratings pr ON pr.product_id = p.id
    LEFT JOIN 
        public.orders o ON o.id = pr.order_id AND o.created_at >= (SELECT max_date FROM last_order_date) - INTERVAL '3 months'
    GROUP BY 
        p.id, pn.name, c.name, pvs.stock, pvp.price, pv.weight, pv.status
)
SELECT 
    SUM(current_stock) AS total_current_stock,
    SUM(total_orders_last_3_months_subquery) AS total_orders_last_3_months
FROM 
    order_data;
