pp_config = dict(
    date = dict(
        type = 'Date_LM',
    ),
    time = dict(
        type = 'Time_LM',
    ),
    receipt_id = dict(
        type = 'Receipt_id_LM',
    ),
    pos_id = dict(
        type = 'Pos_id_LM',
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
    total_money = dict(
        type = 'Money_LM',
        max_words = 5
    )
)