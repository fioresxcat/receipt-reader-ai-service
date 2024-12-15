pp_config = dict(
    mart_name = dict(
        type = 'Martname_LM',
        dict_path = 'dictionaries/bhx_names.txt',
        max_words = None
    ),
    mart_address = dict(
        type = 'Greed_LM'
    ),
    receipt_id = dict(
        type = 'Reciept_id_LM',
        max_words = 1
    ),
    date = dict(
        type = 'Date_LM',
        max_words = 3
    ),
    time = dict(
        type = 'Time_LM',
        max_words = 3
    ),
    staff = dict(
        type = 'Greed_LM'
    ),
    product_name = dict(
        type = 'Greed_LM'
    ),
    product_quantity = dict(
        type = 'Quantity_LM',
        max_words = 1
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
    total_discount_money = dict(
        type = 'Money_LM',
        max_words = 5
    ),
    total_original_money = dict(
        type = 'Money_LM',
        max_words = 5
    )
)