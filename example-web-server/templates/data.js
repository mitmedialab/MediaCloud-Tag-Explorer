var rlDataset = {{reading_level_info['values_json']}};
histogramChart("#mcReadability",rlDataset,400,50,20,{{reading_level_info['final_bucket']}},{{reading_level_info['items_to_show']}},{{reading_level_info['biggest_value']}},10);
