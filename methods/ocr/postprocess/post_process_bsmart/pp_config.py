pp_config = dict(
    mart_name = dict(
        type = 'Greed_LM',
        max_words = None,
        dict_path = 'dictionaries/coopmart_names.txt'
    ),
    mart_location = dict(
        type = 'Greed_LM'
    ),
    tax_code = dict(
        type = 'Greed_LM',
        max_words = 5
    ),
    pos_id = dict(
        type = 'Pos_id_LM'
    ),
    staff = dict(
        type = 'Staff_LM'
    ),
    date = dict(
        type = 'Date_LM',
        max_words = 4
    ),
    time = dict(
        type = 'Time_LM',
        max_words = 3
    ),
    receipt_id = dict(
        type = 'Receipt_id_LM',
    ),
    product_id = dict(
        type = 'Greed_LM',
        max_words = 5
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
        max_words = 3
    ),
    product_total_money = dict(
        type = 'Money_LM',
        max_words = 3
    ),
    product_original_price = dict(
        type = 'Money_LM',
        max_words = 3
    ),
    product_discount_money = dict(
        type = 'Money_LM',
        max_words = 3
    ),
    total_money = dict(
        type = 'Money_LM',
        max_words = 3
    ),
)