pp_config = dict(
    mart_name = dict(
        type = 'Martname_LM',
        dict_path = 'dictionaries/711_names.txt',
        max_words = None
    ),
    pos_id = dict(
        type = 'Pos_id_LM',
        max_words = 2
    ),
    receipt_id = dict(
        type = 'Reciept_id_LM'
    ),
    date = dict(
        type = 'Date_LM',
        max_words = 3
    ),
    time = dict(
        type = 'Time_LM',
        max_words = 3
    ),
    product_name = dict(
        type = 'Greed_LM'
    ),
    product_quantity = dict(
        type = 'Greed_LM'
    ),
    product_unit_price = dict(
        type = 'Greed_LM',
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
    total_discount_money = dict(
        type = 'Money_LM',
        max_words = 5
    ),
    total_quantity = dict(
        type = 'Greed_LM',
    ),
)