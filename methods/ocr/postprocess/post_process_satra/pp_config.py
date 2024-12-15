pp_config = dict(
    mart_name = dict(
        type = 'Martname_LM',
        dict_path = 'dictionaries/satra_names.txt',
        max_words = None
    ),
    tax_code = dict(
        type = 'Greed_LM',
        max_words = 1
    ),
    pos_id = dict(
        type = 'Greed_LM',
        max_words = 1
    ),
    barcode = dict(
        type = 'Barcode_LM'
    ),
    receipt_id = dict(
        type = 'Receipt_id_LM',
        max_words = 5
    ),
    staff = dict(
        type = 'Greed_LM',
        max_words = 1000
    ),
    date = dict(
        type = 'Date_LM',
        max_words = 3
    ),
    time = dict(
        type = 'Time_LM',
        max_words = 2
    ),
    product_id = dict(
        type = 'Product_id_LM',
        max_words = 5
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
    total_money = dict(
        type = 'Money_LM',
        max_words = 5
    ),
)