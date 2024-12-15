pp_config = dict(
    mart_name = dict(
        type = 'Martname_LM',
        dict_path = 'dictionaries/newbigc_names.txt',
        max_words = None
    ),
    mart_location = dict(
        type = 'Greed_LM'
    ),
    tax_code = dict(
        type = 'TaxCode_LM',
        max_words = 1
    ),
    pos_id = dict(
        type = 'Greed_LM'
    ),
    barcode = dict(
        type = 'Barcode_LM'
    ),
    staff = dict(
        type = 'Staff_LM',
        max_words = 3
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
        max_words = 3
    ),
    product_id = dict(
        type = 'Product_id_LM',
        max_words = 1
    ),
    product_vat = dict(
        type = 'Greed_LM',
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
        type = 'Money_LM',
        max_words = 1
    ),
    product_discount_money = dict(
        type = 'Money_LM',
        max_words = 1
    ),
    total_money = dict(
        type = 'Total_Money_LM',
        max_words = None
    ),
    total_original_money = dict(
        type = 'Total_Money_LM',
        max_words = None
    ),
    total_quantity = dict(
        type = 'Greed_LM'
    )
)