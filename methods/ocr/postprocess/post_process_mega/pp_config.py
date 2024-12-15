pp_config = dict(
    mart_name = dict(
        type = 'Martname_LM',
        dict_path = 'dictionaries/mega_names.txt',
        max_words = None
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
        type = 'Pos_id_LM',
        max_words = 1
    ),
    mart_id = dict(
        type = 'Mart_id_LM',
        max_words = 1
    ),
    receipt_id = dict(
        type = 'Receipt_id_LM',
        max_words = 1
    ),
    staff = dict(
        type = 'Greed_LM',
        max_words = 1
    ),
    vat_number = dict(
        type = 'Greed_LM',
        max_words = 1
    ),
    tax_code = dict(
        type = 'TaxCode_LM',
        max_words = None
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
    product_discount_code = dict(
        type = 'ProductDiscountCode_LM',
        max_words = 1
    ),
    product_discount_money = dict(
        type = 'Money_LM',
        max_words = 1
    ),
    total_money = dict(
        type = 'Money_LM',
        max_words = 1
    ),
    total_quantity = dict(
        type = 'Quantity_LM',
        max_words = 1
    ),
)