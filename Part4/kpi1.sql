-- Group Deals
SELECT 
    SUM(o.total_amount) AS total_revenue,
    COUNT(*) AS total_deals,
    AVG(o.total_amount) AS average_revenue_per_group_deal
FROM 
    public.orders o
JOIN 
    public.groups_carts gc ON o.groups_carts_id = gc.id
WHERE 
    gc.status = 'COMPLETED';

-- Single Deals 
SELECT 
    SUM(original_price * quantity) AS net_sales,
    COUNT(*) AS total_deals
FROM 
    public.single_deals
WHERE 
    status = 'ACTIVE';


