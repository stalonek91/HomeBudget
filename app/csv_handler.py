import pandas as pd
import json
import logging


class CSVHandler:

    dict_of_rules = {}

    columns_to_keep = [
            'Data księgowania',
            'Nadawca / Odbiorca',
            'Tytułem', 'Kwota operacji',
            'Typ operacji',
            'Kategoria',
            'Numer referencyjny']
    
    new_column_names = ['date',
                                'receiver',
                                'title',
                                'amount', 
                                'transaction_type',
                                'category',
                                'ref_number'
                                ]

    def __init__(self, df: pd.DataFrame = None) -> None:

        self._load_rules()
        self.df = df
        
        
        
        
    def _load_rules(self):
        try:
            with open('rules_dict.json', 'r') as file:
                CSVHandler.dict_of_rules = json.load(file)
        except FileNotFoundError as e:
            logging.error(f" File not found: {str(e)}")

        except json.JSONDecodeError as e:
            logging.error(f" Error while decoding JSON: {str(e)}")

        except Exception as e:
            logging.error(f" Unexpected error loading rules: {str(e)}")

    def save_rules(self):
        try:
            with open('rules_dict.json', 'w') as file:
                json.dump(CSVHandler.dict_of_rules, file)
                print(f'INFO: Rule JSON file saved succesfully')
        except IOError as e:
            logging.error(f"File I/O error: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error saving rules: {str(e)}")


    def load_csv(self):
            
            if self.df is None:
                logging.error('No DataFrame available to load')
                raise ValueError("DataFrame is not set")
            
            logging.info(f"CSV dataframe loaded successfully")
            return self.df


    def _check_missing_columns(self, df, columns):
        """
        Private helper method to check for missing columns in a DataFrame.
        """

        missing_columns = [col for col in self.columns_to_keep if col not in df.columns]
        if missing_columns:
            logging.error(f"Missing columns in Dataframe: {missing_columns}")
            raise ValueError(f"Missing columns in Dataframe")
        

    def create_df_for_db(self, base_df):
        try:
            base_df.fillna("", inplace=True)
            self._check_missing_columns(df=base_df, columns=self.columns_to_keep)

            new_df = base_df[self.columns_to_keep].copy()
            
            logging.debug("New DataFrame after selecting columns:")
            logging.debug(f'{new_df.head()}')

        except Exception as e:
            logging.error(f"Error processing CSV: {str(e)}")
            return None
        return new_df
    

    def rename_columns(self, last_df):
        try:
            self._check_missing_columns(df=last_df, columns=self.columns_to_keep)

            columns_dict = dict(zip(self.columns_to_keep, self.new_column_names))
            last_df.rename(columns=columns_dict, inplace=True)
            
            last_df['date'] = pd.to_datetime(last_df['date'], format='%d.%m.%Y', errors='coerce')
            last_df['exec_month'] = last_df['date'].dt.strftime('%Y-%m')

            if last_df['exec_month'].isna().any():
                logging.warning(f'Some "exec_month" values could not be parsed and are set to NaT.')
                last_df['exec_month'].fillna('Unknown', inplace=True)
            
            last_df = self.clean_and_format_df(last_df)

        except KeyError as e:
                logging.error(f"KeyError occurred in rename_columns: {str(e)}")
                return None
        except Exception as e:
                logging.error(f'Error occurred in rename_columns: {str(e)}')
                return None
        
        return last_df
    
    
    def clean_and_format_df(self, last_df):
        try:

            last_df.loc[:, 'date'] = pd.to_datetime(last_df['date'], format='%d.%m.%Y', errors='coerce')

            last_df['date'] = last_df['date'].astype('datetime64[ns]')

            if last_df['date'].isna().any():
                logging.warning("Some dates could not be converted and are set to NaT")

            last_df.loc[:, 'date'] = last_df['date'].dt.strftime('%Y-%m-%d')

            last_df['amount'] = last_df['amount'].str.replace(',', '.').str.replace(' ', '').astype(float)

            last_df['exec_month'] = last_df['exec_month'].astype(str)


            if not last_df['ref_number'].is_unique:
                duplicate_values = last_df['ref_number'][last_df['ref_number'].duplicated()].unique()
                logging.error(f"Duplicate ref_number values found: {duplicate_values}")
                raise ValueError(f"The column ref_number contains duplicate values: {duplicate_values}")

            return last_df
        
        except Exception as e:
            logging.error(f'Error occurred clean_and_format_df: {str(e)}')
            return None


    def remove_dupl(self, df):
 
        for category, patterns in CSVHandler.dict_of_rules.items():
            df['receiver'] = df['receiver'].apply(
                lambda x: category if any (pattern in x for pattern in patterns) else x
            )
        return df
    
    def add_rule(self, rule_key, rule_value):
        try:
            if not isinstance(rule_value, str):
                raise ValueError(f"Rule value must be a string. Got  {type(rule_value).__name__} instead")
            CSVHandler.dict_of_rules.setdefault(rule_key, []).append(rule_value)
            self.save_rules()
            logging.info(f"New rule added: {rule_key} -> {rule_value}")
        
        except Exception as e:
            logging.error(f"Error while adding new rule: {str(e)}")
            raise 
            
        
        
       










