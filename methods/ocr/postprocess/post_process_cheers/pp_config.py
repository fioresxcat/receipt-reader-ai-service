pp_config = dict(
    mart_name = dict(
        type = 'Greed_LM'
    ),
    receipt_id = dict(
        type = 'Receipt_id_LM',
        max_words = 10
    ),
    date = dict(
        type = 'Date_LM',
        max_words = 5
    ),
    time = dict(
        type = 'Time_LM',
        max_words = 5
    ),
    staff = dict (
        type = 'Staff_LM'
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
        max_words = 5
    ),
    product_total_money = dict(
        type = 'Money_LM',
        max_words = 5
    ),
    total_money = dict(
        type = 'Money_LM',
        max_words = 5
    ),
    total_quantity = dict(
        type = 'Quantity_LM',
        max_words = 3
    ),
)