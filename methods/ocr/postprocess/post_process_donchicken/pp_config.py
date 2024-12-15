pp_config = dict(
    # mart_name = dict(
    #     type = 'Martname_LM',
    #     dict_path = 'dictionaries/newgs25_names.txt',
    #     max_words = None
    # ),
    mart_name = dict(
        type = 'Greed_LM'
    ),
    receipt_id = dict(
        type = 'Receipt_id_LM',
        max_words = 5
    ),
    staff = dict(
        type = 'Staff_LM',
        max_words = 10
    ),
    date = dict(
        type = 'Date_LM',
        max_words = 4
    ),
    time = dict(
        type = 'Time_LM',
        max_words = 4
    ),
    product_name = dict(
        type = 'Greed_LM'
    ),
    product_quantity = dict(
        type = 'Quantity_LM',
        max_words = 2
    ),
    second_product_name = dict(
        type = 'Greed_LM'
    ),
    product_total_money = dict(
        type = 'Money_LM',
        max_words = 3
    ),
    total_money = dict(
        type = 'Money_LM',
        max_words = 3
    ),
    total_original_money = dict(
        type = 'Money_LM',
        max_words = 3
    ),
    total_discount_money = dict(
        type = 'Money_LM',
        max_words = 3
    )
)