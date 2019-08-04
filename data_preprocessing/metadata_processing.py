import os
import pandas


def merge_columns(column_a, column_b):
    new_column = []
    for a, b in zip(column_a, column_b):
        if a == b:
            new_column.append(a)
        elif a == 1 or b == 1:
            new_column.append(1)
    return new_column


def column(column_name, dataFrame):
    return dataFrame[column_name].values


def metadata_processing():
    print('>>> PROCESSING METADATA <<<')

    df = pandas.read_csv('annotations_final.csv', sep=None, engine='python')
    rock = pandas.Series(
        merge_columns(column('rock', df), merge_columns(column('hard rock', df), column('soft rock', df))))
    classical = pandas.Series(
        merge_columns(column('clasical', df), merge_columns(column('classical', df), column('classic', df))))
    electronic = pandas.Series(
        merge_columns(column('electronic', df), merge_columns(column('electronica', df), column('electro', df))))

    d = {'clip_id': column('clip_id', df),
         'rock': rock,
         'classical': classical,
         'electronic': electronic,
         'mp3_path': column('mp3_path', df)}
    metadata = pandas.DataFrame(data=d)

    # drop all rows with only zeros
    metadata = metadata[(metadata.drop('clip_id', axis=1).T != 0).any()]
    # drop all rows with multiple labels
    metadata = metadata[(metadata.drop(['clip_id', 'mp3_path'], axis=1).T.sum() == 1)]

    # remove corrupted files
    metadata = metadata[metadata[
                            'mp3_path'] != '9/american_baroque-dances_and_suites_of_rameau_and_couperin-25-le_petit_rien_xiveme_ordre_couperin-88-117.mp3']
    metadata = metadata[metadata[
                            'mp3_path'] != '8/jacob_heringman-josquin_des_prez_lute_settings-19-gintzler__pater_noster-204-233.mp3']

    metadata.to_csv('data/metadata_processed.csv', index=False)
    print('>>> SAVED TO: data/metadata_processed.csv <<<')

    os.remove('annotations_final.csv')
    print('>>> DONE <<<\n')
