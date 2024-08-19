import pandas as pd
import json



class CSVHandler:

    dict_of_rules = {}

    def __init__(self, df: pd.DataFrame = None) -> None:

        self.load_rules()

        

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
        
    def load_rules(self):
        try:
            with open('rules_dict.json', 'r') as file:
                CSVHandler.dict_of_rules = json.load(file)
        except Exception as e:
            print(f'ERROR: Something went wrong loading the json file with rules. Details: {str(e)}')

    def save_rules(self):
        with open('rules_dict.json', 'w') as file:
            json.dump(CSVHandler.dict_of_rules, file)
            print(f'INFO: Rule JSON file saved succesfully')


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


    def remove_dupl(self, df):
 
        for category, patterns in CSVHandler.dict_of_rules.items():
            df['receiver'] = df['receiver'].apply(
                lambda x: category if any (pattern in x for pattern in patterns) else x
            )
        return df
    
    def add_rule(self, rule_key, rule_value):
        if rule_key in CSVHandler.dict_of_rules:
            CSVHandler.dict_of_rules[rule_key].append(rule_value)
        else:
            CSVHandler.dict_of_rules[rule_key] = [rule_value]
        self.save_rules()
        print(f"New rule added: {rule_key} -> {rule_value}")










