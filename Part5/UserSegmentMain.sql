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
ORDER BY 
    total_order_amount DESC;  -- Order by total amount in descending order