pp_config = dict(
    mart_name = dict(
        type = 'Martname_LM',
        dict_path = 'dictionaries/nguyenkim_names.txt',
        max_words = None
    ),
    mart_id = dict(
        type = 'Greed_LM',
        max_words = None
    ),
    store_id = dict(
        type = 'Greed_LM',
        max_words = None
    ),
    date = dict(
        type = 'Date_LM',
        max_words = None
    ),
    time = dict(
        type = 'Time_LM',
        max_words = None
    ),
    receipt_id = dict(
        type = 'Greed_LM'
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
    )
)