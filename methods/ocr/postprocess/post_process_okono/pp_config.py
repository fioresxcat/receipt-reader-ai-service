pp_config = dict(
    mart_name = dict(
        type = 'Greed_LM',
        max_words = None
    ),
    pos_id = dict(
        type = 'Pos_id_LM',
        max_words = 1
    ),
    staff = dict(
        type = 'Greed_LM'
    ),
    date = dict(
        type = 'Date_LM',
        max_words = 1
    ),
    time = dict(
        type = 'Time_LM',
        max_words = 1
    ),
    receipt_id = dict(
        type = 'Receipt_id_LM',
        max_words = None
    ),
    product_name = dict(
        type = 'Greed_LM'
    ),
    product_quantity = dict(
        type = 'Greed_LM'
    ),
    product_unit_price = dict(
        type = 'Money_LM',
        max_words = 5
    ),
    product_total_money = dict(
        type = 'Money_LM',
        max_words = 5
    ),
    product_original_price = dict(
        type = 'Money_LM',
        max_words = 5
    ),
    total_money = dict(
        type = 'Money_LM',
        max_words = 5
    ),
    total_original_money = dict(
        type = 'Money_LM',
        max_words = 5
    ),
    total_discount_money = dict(
        type = 'Money_LM',
        max_words = 5
    ),
    total_quantity = dict(
        type = 'Greed_LM',
        max_words = 1
    ),
)