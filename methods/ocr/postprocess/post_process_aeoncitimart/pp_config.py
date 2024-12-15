pp_config = dict(
    mart_name = dict(
        type = 'Martname_LM',
        dict_path = 'dictionaries/aeon_names.txt',
        max_words = None
    ),
    pos_id = dict(
        type = 'Pos_id_LM',
        max_words = 1
    ),
    staff = dict(
        type = 'Greed_LM',
        max_words = 1000
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
        max_words = 1
    ),
    product_id = dict(
        type = 'Product_id_LM',
        max_words = 1
    ),
    product_name = dict(
        type = 'ProductName_LM',
        max_words = None,
        dict_path = 'dictionaries/dictionary.txt'
    ),
    product_quantity = dict(
        type = 'Quantity_LM',
        max_words = 1
    ),
    product_unit_price = dict(
        type = 'Money_LM',
        max_words = 1
    ),
    product_total_money = dict(
        type = 'Money_LM',
        max_words = 1
    ),
    product_original_price = dict(
        type = 'Product_Original_Price_LM',
        max_words = 1
    ),
    product_discount_money = dict(
        type = 'Money_LM',
        max_words = 2
    ),
    total_money = dict(
        type = 'Money_LM',
        max_words = 1
    ),
    total_discount_money = dict(
        type = 'Money_LM',
        max_words = 1
    ),
    total_quantity = dict(
        type = 'Quantity_LM',
        max_words = 1
    ),
)