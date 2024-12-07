WITH CompletedOrders AS (
    SELECT 
        COUNT(*) AS completed_order_count
    FROM 
        orders
    WHERE 
        status = 'COMPLETED'  -- Use the correct status value here
),
TotalGroupDeals AS (
    SELECT 
        COUNT(*) AS total_group_deal_count
    FROM 
        group_deals
)

SELECT 
    COALESCE(c.completed_order_count, 0) AS completed_orders,
    COALESCE(t.total_group_deal_count, 0) AS total_group_deals,
    CASE 
        WHEN COALESCE(t.total_group_deal_count, 0) = 0 THEN 0
        ELSE COALESCE(c.completed_order_count, 0) * 1.0 / t.total_group_deal_count
    END AS conversion_rate
FROM 
    CompletedOrders c,
    TotalGroupDeals t;