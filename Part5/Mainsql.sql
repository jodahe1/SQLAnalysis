SELECT 
    o.id AS order_id,
    o.groups_carts_id,
    o.status AS order_status,
    o.total_amount,
    o.created_at AS order_created_at,
    o.updated_at AS order_updated_at,
    o.deleted_at AS order_deleted_at,
    o.payment_method,
    o.discount,
    pr.rating,
    pr.comment,
    pn.id AS product_name_id,
    pn.name AS product_name,
    c.id AS category_id,
    c.name AS category_name,
    p.id AS product_id,
    p.vendor_id,
    p.status AS product_status,
    p.created_at AS product_created_at,
    p.updated_at AS product_updated_at,
    p.deleted_at AS product_deleted_at,
    pvs.id AS variation_stock_id,
    pvs.stock,
    pvp.id AS variation_price_id,
    pvp.price,
    pv.id AS product_variation_id,
    pv.weight,
    pv.status AS variation_status
FROM 
    public.orders o
JOIN 
    public.product_ratings pr ON o.id = pr.order_id
JOIN 
    public.products p ON pr.product_id = p.id
JOIN 
    public.product_names pn ON p.name_id = pn.id
JOIN 
    public.categories c ON pn.category_id = c.id
JOIN 
    public.product_variations pv ON p.id = pv.product_id
JOIN 
    public.product_variation_stocks pvs ON pv.id = pvs.product_variation_id
JOIN 
    public.product_variation_prices pvp ON pv.id = pvp.product_variation_id;