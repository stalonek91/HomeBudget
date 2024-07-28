import pandas as pd



class CSVHandler:

    def __init__(self, df: pd.DataFrame) -> None:

        self.df = df
        self.columns_to_keep = [
            'Data księgowania',
            'Nadawca / Odbiorca',
            'Tytułem', 'Kwota operacji',
            'Typ operacji',
            'Kategoria',
            'Numer referencyjny']
        
        self.new_column_names = ['date',
                                'receiver',
                                'title',
                                'amount', 
                                'transaction_type',
                                'category',
                                'ref_number']

    def load_csv(self):
        try:
            print('CSV file loaded succesfully')
            return self.df
        except Exception as e:
            print(f'Error occurred: {str(e)}')
            return None
        
    def create_df_for_db(self, base_df):
        try:
            base_df.fillna("", inplace=True)
            new_df = base_df[self.columns_to_keep].copy()
        except Exception as e:
            print(f'Error occurred: {str(e)}')
            return None
        return new_df
    

    def rename_columns(self, last_df):
        try:
            columns_dict = dict(zip(self.columns_to_keep, self.new_column_names))
            last_df.rename(columns=columns_dict, inplace=True)
            last_df = self.clean_and_format_df(last_df)
        except Exception as e:
                print(f'Error occurred: {str(e)}')
                return None
        return last_df
    
    
    def clean_and_format_df(self, last_df):
        try:

            last_df.loc[:, 'date'] = pd.to_datetime(last_df['date'], format='%d.%m.%Y', errors='coerce')
            last_df['date'] = last_df['date'].astype('datetime64[ns]')

            if last_df['date'].isna().any():
                print("Some dates could not be converted and are set to NaT")

            last_df.loc[:, 'date'] = last_df['date'].dt.strftime('%Y-%m-%d')
            last_df['amount'] = last_df['amount'].str.replace(',', '.').str.replace(' ', '').astype(float)


            if not last_df['ref_number'].is_unique:
                duplicate_values = last_df['ref_number'][last_df['ref_number'].duplicated()].unique()
                raise ValueError(f"The column ref_number contains duplicate values: {duplicate_values}")

            return last_df
        
        except Exception as e:
            print(f'Error occurred: {str(e)}')
            return None

            

            

        




        except Exception as e:
            print(f'Error occurred: {str(e)}')
            return None
        return last_df









