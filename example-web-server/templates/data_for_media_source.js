updateFilteredInfo("{{media_name}}",{{story_count}});

var rlDataset = {{reading_level_info['values_json']}};
histogramChart("#mcFilteredReadability",rlDataset,400,50,20,{{reading_level_info['final_bucket']}},{{reading_level_info['items_to_show']}},{{reading_level_info['biggest_value']}},10);

$('#mcFilteredResults').show();
