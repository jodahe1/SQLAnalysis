SELECT 
    gc.id AS group_cart_id,
    gc.group_id,
    o.id AS order_id,
    o.groups_carts_id,
    o.status AS order_status,
    o.total_amount,
    o.created_at AS order_created_at,
    gcv.id AS group_cart_variation_id,
    gcv.product_variation_id,
    pv.id AS variation_id,
    pv.product_id,
    p.id AS product_id,
    p.name_id,
    pn.id AS product_name_id,
    pn.name AS product_name,
    pn.category_id,
    c.id AS category_id,
    c.name AS category_name
FROM 
    public.groups_carts gc
JOIN 
    public.orders o 
    ON gc.id = o.groups_carts_id
JOIN 
    public.group_cart_variations gcv
    ON gc.id = gcv.group_cart_id
JOIN 
    public.product_variations pv
    ON gcv.product_variation_id = pv.id
JOIN 
    public.products p
    ON pv.product_id = p.id
JOIN 
    public.product_names pn
    ON p.name_id = pn.id
JOIN 
    public.categories c
    ON pn.category_id = c.id
WHERE 
    o.created_at BETWEEN '2024-06-16 17:52:36.368747' AND '2024-09-14 17:52:36.368747';
