SELECT 
    pvs.id AS stock_id,
    pvs.stock AS current_stock,
    pvp.price AS current_price,
    pv.id AS product_variation_id,
    p.id AS product_id,
    pn.name AS product_name,
    c.name AS category_name,
    pr.rating AS product_rating,
    o.id AS order_id,
    o.total_amount AS order_total,
    o.created_at AS order_date
FROM 
    product_variation_stocks pvs
JOIN 
    product_variations pv ON pvs.product_variation_id = pv.id
JOIN 
    products p ON pv.product_id = p.id
JOIN 
    product_names pn ON p.name_id = pn.id
JOIN 
    categories c ON pn.category_id = c.id
LEFT JOIN 
    product_variation_prices pvp ON pvs.product_variation_id = pvp.product_variation_id
LEFT JOIN 
    product_ratings pr ON p.id = pr.product_id
LEFT JOIN 
    orders o ON pr.order_id = o.id;
