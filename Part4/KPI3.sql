-- Conversion Rate for Group Deals

SELECT 
    (COUNT(DISTINCT g.id) * 100.0 / NULLIF(COUNT(DISTINCT gd.id), 0)) AS conversion_rate
FROM 
    public.group_deals gd
LEFT JOIN 
    public.groups g ON g.group_deals_id = gd.id
WHERE 
    g.status = 'COMPLETED';
