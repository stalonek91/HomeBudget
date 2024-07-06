import pandas as pd
import os
import csv


class CSVHandler:

    def __init__(self, file_path: str) -> None:

        self.file_path = file_path


    def validate_csv(self):
        if not self.file_path.lower().endswith('.csv'):
            print('Provided file does not have a .csv extension')
            return False
        
        if os.path.getsize(self.file_path) == 0:
            print(f'File is empty!')
            return False
        
        try:
            with open(self.file_path, 'r') as file:
                sample = csv.Sniffer().sniff(file.read(1024))
                file.seek(0)
                reader = csv.reader(file, delimiter=sample.delimiter)
                headers = next(reader, None)
                if headers is None or len(headers) < 2:
                    print('The file does not appear to be a valid CSV file')
                    return False
                
        except Exception as e:
            print(f'An error occurred while checking the file: {str(e)}')
            return False
        
        return True



    def load_csv(self):
        try:
            df = pd.read_csv(self.file_path, delimiter=';')
            print('CSV file loaded succesfully')
            return df
        except pd.errors.EmptyDataError:
            print('The file is empty!')
            return None
        except pd.errors.ParserError:
            print('The file is not a valid CSV file or is malformed!')
            return None
        except FileNotFoundError:
            print ("The file was not found. Please check file location and try again")
            return None
        except Exception as e:
            print(f'Error occurred: {str(e)}')
            return None
        





