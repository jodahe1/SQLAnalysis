WITH UserOrderStats AS (
    SELECT 
        gc.user_id,
        COUNT(o.id) AS order_count,
        SUM(o.total_amount) AS total_order_amount
    FROM 
        public.orders o
    JOIN 
        public.groups_carts gc ON o.groups_carts_id = gc.id
    GROUP BY 
        gc.user_id
),
AverageStats AS (
    SELECT 
        AVG(order_count) AS avg_order_count,
        AVG(total_order_amount) AS avg_total_order_amount
    FROM 
        UserOrderStats
)

SELECT 
    uos.user_id,
    uos.order_count,
    uos.total_order_amount,
    CASE 
        WHEN uos.order_count > avg.avg_order_count AND uos.total_order_amount > avg.avg_total_order_amount THEN 'valuable user'
        WHEN uos.order_count > avg.avg_order_count OR uos.total_order_amount > avg.avg_total_order_amount THEN 'normal user'
        ELSE 'rarely user'
    END AS user_category
FROM 
    UserOrderStats uos,
    AverageStats avg
ORDER BY 
    uos.total_order_amount DESC;  -- Order by total amount in descending order