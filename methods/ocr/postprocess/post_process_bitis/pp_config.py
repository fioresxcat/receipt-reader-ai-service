pp_config = dict(
    mart_name = dict(
        type = 'Greed_LM',
        max_words = None
    ),
    address = dict(
        type = 'Greed_LM',
        max_words = None
    ),
    receipt_id = dict(
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
    product_name = dict(
        type = 'ProductName_LM',
        max_words = None
    ),
    product_unit_price = dict(
        type = 'Money_LM',
        max_words = 5
    ),
    product_quantity = dict(
        type = 'Quantity_LM',
        max_words = None
    ),
    product_total_money = dict(
        type = 'Money_LM',
        max_words = 5
    ),
    total_quantity = dict(
        type = 'Quantity_LM',
        max_words = None
    ),
    total_money = dict(
        type = 'Money_LM',
        max_words = 5
    ),
    product_discount_retail_money = dict(
        type = 'Money_LM',
        max_words = 5
    ),
    product_discount_wholesale_money = dict(
        type = 'Money_LM',
        max_words = 5
    )
)