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
        type = 'Greed_LM'
    ),
    staff = dict(
        type = 'Greed_LM'
    ),
    date = dict(
        type = 'Greed_LM',
        max_words = 1
    ),
    time = dict(
        type = 'Greed_LM',
        max_words = 1
    ),
    receipt_id = dict(
        type = 'Greed_LM',
        max_words = 1
    ),
    product_id = dict(
        type = 'Greed_LM',
        max_words = 5
    ),
    product_name = dict(
        type = 'Greed_LM'
    ),
    product_vat = dict(
        type = 'Greed_LM',
        max_words = 5
    ),
    product_quantity = dict(
        type = 'Greed_LM'
    ),
    product_unit_price = dict(
        type = 'Greed_LM',
        max_words = 5
    ),
    product_total_money = dict(
        type = 'Greed_LM',
        max_words = 5
    ),
    product_original_price = dict(
        type = 'Greed_LM',
        max_words = 5
    ),
    product_discount_money = dict(
        type = 'Greed_LM',
        max_words = 5
    ),
    product_down_money = dict(
        type = 'Greed_LM',
        max_words = 5
    ),
    total_money = dict(
        type = 'Greed_LM',
        max_words = 5
    ),
    total_quantity = dict(
        type = 'Greed_LM',
        max_words = 1
    ),
)