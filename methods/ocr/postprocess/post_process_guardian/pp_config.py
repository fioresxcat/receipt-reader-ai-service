pp_config = dict(
    mart_name = dict(
        type = 'Mart_id_LM',
        max_words = 1
    ),
    receipt_id = dict(
        type = 'Receipt_id_LM',
        max_words = 3
    ),
    date = dict(
        type = 'Date_LM',
        max_words = 3
    ),
    time = dict(
        type = 'Time_LM',
        max_words = 2
    ),
    product_id = dict(
        type = 'Product_id_LM',
        max_words = 3
    ),
    product_quantity = dict(
        type = 'Product_quantity_LM',
        max_words = 1
    ),
    product_name = dict(
        type = 'Greed_LM'
    ),
    product_total_money = dict(
        type = 'Money_LM',
        max_words = 5
    ),
    product_vat = dict(
        type = 'Greed_LM'
    ),
    product_return = dict(
        type = 'Greed_LM'
    ),
    product_unit_price = dict(
        type = 'Money_LM',
        max_words = 5
    ),
    product_discount_money = dict(
        type = 'Money_LM',
        max_words = 5
    ),
    total_money = dict(
        type = 'Money_LM',
        max_words = 5
    ),
    total_discount_money = dict(
        type = 'Money_LM',
        max_words = 5
    ),
    staff = dict(
        type = 'Staff_LM',
        max_words = 5
    ),
    pos_id = dict(
        type = 'Pos_id_LM',
        max_words = 3
    )
)