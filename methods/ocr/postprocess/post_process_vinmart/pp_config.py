pp_config = dict(
    mart_name = dict(
        type = 'Greed_LM',
        max_words = None,
        dict_path = 'dictionaries/vinmart_names.txt'
    ),
    date = dict(
        type = 'Date_LM',
        max_words = 1
    ),
    time = dict(
        type = 'Time_LM',
        max_words = 1
    ),
    pos_id = dict(
        type = 'Counter_id_LM',
        max_words = 5
    ),
    staff = dict(
        type = 'Staff_LM',
        max_words = 5
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
        type = 'Quantity_LM'
    ),
    product_unit_price = dict(
        type = 'Money_LM',
        max_words = 5
    ),
    product_total_money = dict(
        type = 'Money_LM',
        max_words = 5
    ),
    product_discount_money = dict(
        type = 'Discount_Money_LM',
        max_words = 5
    ),
    total_money = dict(
        type = 'Money_LM',
        max_words = 5
    ),
    total_discount_money = dict(
        type = 'Discount_Money_LM',
        max_words = 5
    ),
    total_quantity = dict(
        type = 'Quantity_LM'
    ),
)