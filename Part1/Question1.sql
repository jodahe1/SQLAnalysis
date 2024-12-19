-- Write a SQL query to fetch the top 10 users who contributed the highest revenue 
--within the last 30 days, along with the number of groups they participated in and 
--the categories of products they purchased.

WITH UserRevenue AS (
    SELECT 
        gc.user_id,
        SUM(o.total_amount) AS total_revenue,
        COUNT(DISTINCT g.id) AS group_count
    FROM 
        orders o
    JOIN 
        groups_carts gc ON o.groups_carts_id = gc.id
    JOIN 
        groups g ON gc.group_id = g.id
    WHERE 
        o.created_at >= NOW() - INTERVAL '60 days' 
        AND o.status = 'COMPLETED' 
    GROUP BY 
        gc.user_id
),
UserCategories AS (
    SELECT 
        u.id AS user_id,
        ARRAY_AGG(DISTINCT c.name) AS categories
    FROM 
        users u
    JOIN 
        groups_carts gc ON u.id = gc.user_id
    JOIN 
        groups g ON gc.group_id = g.id
    JOIN 
        group_deals gd ON g.group_deals_id = gd.id
    JOIN 
        products p ON gd.product_id = p.id
    JOIN 
        product_names pn ON p.name_id = pn.id
    JOIN 
        categories c ON pn.category_id = c.id
    GROUP BY 
        u.id
)
SELECT 
    u.user_id,
	usr.name,
    u.total_revenue,
    u.group_count,
    uc.categories
    
FROM 
    UserRevenue u
LEFT JOIN 
    UserCategories uc ON u.user_id = uc.user_id
JOIN 
    users usr ON u.user_id = usr.id
ORDER BY 
    u.total_revenue DESC
LIMIT 10;
