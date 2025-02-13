pp_config = dict(
    mart_name = dict(
        type = 'Value_LM',
        max_words = None,
        dict_path = 'dictionaries/emart_names.txt'
    ),
    mart_location = dict(
        type = 'Greed_LM'
    ),
    tax_code = dict(
        type = 'Greed_LM',
        max_words = 5
    ),
    barcode = dict(
        type = 'Barcode_LM',
        max_words = 5
    ),
    pos_id = dict(
        type = 'Pos_id_LM',
        max_words = 2
    ),
    staff = dict(
        type = 'Staff_LM', 
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
    receipt_id = dict(
        type = 'Receipt_id_LM',
        max_words = 1
    ),
    product_id = dict(
        type = 'Greed_LM',
        max_words = 5
    ),
    product_name = dict(
        type = 'Greed_LM'
    ),
    product_vat = dict(
        type = 'Greed_LM',
        max_words = 5
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
    product_original_price = dict(
        type = 'Money_LM',
        max_words = 5
    ),
    product_discount_money = dict(
        type = 'Money_LM',
        max_words = 5
    ),
    product_down_money = dict(
        type = 'Money_LM',
        max_words = 5
    ),
    total_money = dict(
        type = 'Money_LM',
        max_words = 5
    ),
    total_original_money = dict(
        type = 'Money_LM',
        max_words = 5
    ),
    total_discount_money  = dict(
        type = 'Money_LM',
        max_words = 5
    ),
    total_quantity = dict(
        type = 'Total_Quantity_LM',
        max_words = 2
    ),
)