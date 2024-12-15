pp_config = dict(
    mart_name = dict(
        type = 'Martname_LM',
        max_words = None,
        dict_path = None
    ),
    pos_id = dict(
        type = 'Pos_id_LM',
        max_words = 2
    ),
    staff = dict(
        type = 'Greed_LM'
    ),
    date = dict(
        type = 'Date_LM',
        max_words = 3
    ),
    time = dict(
        type = 'Time_LM',
        max_words = 2
    ),
    receipt_id = dict(
        type = 'Receipt_id_LM',
        max_words = 1
    ),
    product_name = dict(
        type = 'Greed_LM'
    ),
    product_quantity = dict(
        type = 'Quantity_LM',
        max_words = 2
    ),
    product_unit_price = dict(
        type = 'Money_LM',
        max_words = 2
    ),
    product_total_money = dict(
        type = 'Money_LM',
        max_words = 2
    ),
    product_original_price = dict(
        type = 'Money_LM',
        max_words = 2
    ),
    product_discount_money = dict(
        type = 'Money_LM',
        max_words = 2
    ),
    total_money = dict(
        type = 'Money_LM',
        max_words = 2
    ),
)