pp_config = dict(
    mart_name = dict(
        type = 'Martname_LM',
        dict_path = 'dictionaries/lotte_names.txt',
        max_words = None
    ),
    tax_code = dict(
        type = 'TaxCode_LM',
        max_words = None
    ),
    pos_id = dict(
        type = 'Pos_id_LM',
        max_words = None
    ),
    staff = dict(
        type = 'Staff_LM',
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
        type = 'Greed_LM',
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
    product_vat = dict(
        type = 'VAT_LM',
        max_words = 1
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
    product_discount_money = dict(
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
        type = 'Quantity_LM',
        max_words = 1
    ),
)