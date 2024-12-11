WITH UserCartCounts AS (
    SELECT 
        u.id AS user_id,
        COUNT(c.id) AS cart_count
    FROM 
        users u
    LEFT JOIN 
        carts c ON u.id = c.user_id
    GROUP BY 
        u.id
),
AverageCartCount AS (
    SELECT 
        AVG(cart_count) AS avg_cart_count
    FROM 
        UserCartCounts
)

SELECT 
    ucc.user_id,
    ucc.cart_count,
    CASE 
        WHEN ucc.cart_count < ac.avg_cart_count THEN 'below average'
        ELSE 'above average'
    END AS occurrence_category
FROM 
    UserCartCounts ucc,
    AverageCartCount ac
ORDER BY 
    ucc.cart_count DESC;  -- Ordering by cart_count in descending order