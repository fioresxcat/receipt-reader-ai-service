pp_config = dict(
    mart_name = dict(
        type = 'Greed_LM',
        max_words = None
    ),
    staff = dict(
        type = 'Greed_LM',
        max_words = None
    ),
    date = dict(
        type = 'Date_LM',
        max_words = 2
    ),
    time = dict(
        type = 'Time_LM',
        max_words = 2
    ),
    receipt_id = dict(
        type = 'Receipt_id_LM',
        max_words = 1
    ),
    product_id = dict(
        type = 'Greed_LM',
        max_words = None
    ),
    product_name = dict(
        type = 'Greed_LM',
        max_words = None
    ),
    product_quantity = dict(
        type = 'Quantity_LM',
        max_words = 1
    ),
    product_unit_price = dict(
        type = 'Money_LM',
        max_words = 2
    ),
    product_total_money = dict(
        type = 'Money_LM',
        max_words = 2
    ),
    total_money = dict(
        type = 'Money_LM',
        max_words = 2
    ),
    total_original_money = dict(
        type = 'Money_LM',
        max_words = 2
    ),
)