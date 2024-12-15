pp_config = dict(
    mart_name = dict(
        type = 'Value_LM',
        max_words = None,
        dict_path = 'dictionaries/coopmart_names.txt'
    ),
    mart_address = dict(
        type = 'Greed_LM'
    ),
    receipt_tax_number = dict(
        type = 'Greed_LM'
    ),
    tax_code = dict(
        type = 'TaxCode_LM',
        max_words = 5
    ),
    pos_id = dict(
        type = 'Pos_id_LM',
        max_words = 2
    ),
    staff = dict(
        type = 'Greed_LM'
    ),
    barcode = dict(
        type = 'Barcode_LM'
    ),
    date = dict(
        type = 'Date_LM',
        max_words = 1
    ),
    time = dict(
        type = 'Time_LM',
        max_words = 3
    ),
    receipt_id = dict(
        type = 'Receipt_id_LM',
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
        max_words = 5
    ),
    product_quantity = dict(
        type = 'Quantity_LM',
        max_words = 2
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
        type = 'Discount_Money_LM',
        max_words = 1
    ),
    product_down_money = dict(
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