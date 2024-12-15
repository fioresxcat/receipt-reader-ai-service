pp_config = dict(
    mart_name = dict(
        type = 'Greed_LM',
        # dict_path = 'dictionaries/family_names.txt',
        # max_words = None
    ),
    pos_id = dict(
        type = 'Pos_id_LM',
        max_words = 2
    ),
    receipt_id = dict(
        type = 'Receipt_id_LM',
        max_words = 10
    ),
    date = dict(
        type = 'Date_LM',
        max_words = 3
    ),
    time = dict(
        type = 'Time_LM',
        max_words = 3
    ),
    staff = dict (
        type = 'Greed_LM'),
    product_name = dict(
        type = 'ProductName_LM',
        max_words = 20
    ),
    product_quantity = dict(
        type = 'Quantity_LM',
        max_words = 2
    ),
    product_unit_price = dict(
        type = 'Money_LM',
        max_words = 5
    ),
    product_discount_money = dict(
        type = 'Discount_Money_LM',
        max_words = 5
    ),
    product_total_money = dict(
        type = 'Money_LM',
        max_words = 5
    ),
    total_quantity = dict(
        type = 'Quantity_LM'
    ),
    total_money = dict(
        type = 'Money_LM',
        max_words = 5
    ),
    total_discount_money = dict(
        type = 'Discount_Money_LM',
        max_words = 5
    ),
    total_original_money = dict(
        type = 'Money_LM',
        max_words = 5
    )
)