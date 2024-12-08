SELECT 
    c.name AS category_name,
    v.phone AS vendor_phone,
    SUM(o.total_amount) AS total_order_contribution
FROM 
    public.product_names pn
LEFT JOIN 
    public.categories c ON pn.category_id = c.id
LEFT JOIN 
    public.products p ON pn.id = p.name_id
LEFT JOIN 
    public.vendors v ON p.vendor_id = v.id
JOIN 
    public.product_ratings pr ON p.id = pr.product_id
JOIN 
    public.orders o ON pr.order_id = o.id
WHERE 
    o.deleted_at IS NULL  -- Ensure we only consider non-deleted orders
GROUP BY 
    c.name, v.phone
ORDER BY 
    c.name, v.phone;