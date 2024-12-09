SELECT 
    AVG(o.total_amount) AS average_revenue_per_group_deal
FROM 
    public.orders o
JOIN 
    public.groups_carts gc ON o.groups_carts_id = gc.id
WHERE 
    gc.status='COMPLETED';  