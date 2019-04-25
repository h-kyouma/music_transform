import pandas

def merge_columns(column_a,column_b):
    new_column = []
    for a, b in zip(column_a, column_b):
        if(a == b): new_column.append(a)
        elif(a == 1 or b == 1): new_column.append(1)
    return new_column

def column(column_name, dataFrame = pandas.read_csv('annotations_final.csv',
                                                    sep=None, engine='python')):
    return dataFrame[column_name].values

def metadata_processing():
    print('\n>>> PROCESSING METADATA <<<')
    
    rock = pandas.Series(merge_columns(column('rock'),merge_columns(column('hard rock'),column('soft rock'))))
    classical = pandas.Series(merge_columns(column('clasical'),merge_columns(column('classical'),column('classic'))))
    electronic = pandas.Series(merge_columns(column('electronic'),merge_columns(column('electronica'),column('electro'))))
    
    d = {'clip_id':column('clip_id'), 
         'rock':rock, 
         'classical':classical, 
         'electronic':electronic, 
         'mp3_path':column('mp3_path')}
    metadata = pandas.DataFrame(data = d)
    
    # drop all rows with only zeros
    metadata = metadata[(metadata.drop('clip_id', axis=1).T != 0).any()]
    #drop all rows with multiple labels
    metadata = metadata[((metadata.drop(['clip_id', 'mp3_path'], axis=1).T).sum() == 1)]
    
    metadata.to_csv('metadata_processed.csv', index=False)
    print('>>> SAVED TO: metadata_processed.csv <<<')
    
    print('>>> DONE <<<')
