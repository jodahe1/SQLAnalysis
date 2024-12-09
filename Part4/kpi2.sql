SELECT 
    (SELECT COUNT(*) FROM public.users) AS total_users,
    (SELECT COUNT(DISTINCT user_id) FROM public.groups_carts) AS distinct_users_in_cart,
    ROUND(
        (SELECT COUNT(DISTINCT user_id) FROM public.groups_carts)::decimal / 
        (SELECT COUNT(*) FROM public.users) * 100, 2
    ) AS participation_rate
;
