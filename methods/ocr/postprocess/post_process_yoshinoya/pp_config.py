pp_config = dict(
    mart_name = dict(
        type = 'Greed_LM',
    ),
    date = dict(
        type = 'Date_LM',
    ),
    time = dict(
        type = 'Time_LM',
    ),
    staff = dict(
        type = 'Receipt_id_LM',
    ),
    receipt_id = dict(
        type = 'Receipt_id_LM',
    ),
    product_name = dict(
        type = 'Greed_LM'
    ),
    product_quantity = dict(
        type = 'Greed_LM'
    ),
    product_total_money = dict(
        type = 'Money_LM',
        max_words = 5
    ),
    total_original_money = dict(
        type = 'Money_LM',
        max_words = 5
    ),
    total_money = dict(
        type = 'Money_LM',
        max_words = 5
    )
)