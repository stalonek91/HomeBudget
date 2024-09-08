import pandas as pd
import json
import pytest
from unittest.mock import mock_open, patch

from app.csv_handler import CSVHandler

@pytest.fixture(autouse=True)
def reset_dict_of_rules():
    CSVHandler.dict_of_rules = {}


def test_init_with_valid_arguments():
    #Arrange

    test_df = df = pd.DataFrame({
    'column1': [1, 2, 3],
    'column2': ['A', 'B', 'C']})


    #Act

    handler = CSVHandler(test_df)

    assert isinstance(handler.df, pd.DataFrame)
    assert handler.df.equals(test_df)

def test_load_rules_success():
    # Simulate the file content with valid JSON

    mock_file_content = json.dumps({"Wycieczki/Hotel": ["BOOKING", "PARKHOTEL"]})

    with patch("builtins.open", mock_open(read_data=mock_file_content)):
        handler = CSVHandler()

        # Assert that dict_of_rules has been loaded correctly
        assert CSVHandler.dict_of_rules == {"Wycieczki/Hotel": ["BOOKING", "PARKHOTEL"]}

def test_load_rules_JSONDecode_error():
    
    invalid_json = "{'key': 'value'}"

    with patch("builtins.open", mock_open(read_data=invalid_json)):
        
        with patch("json.load", side_effect=json.JSONDecodeError("Expecting value", "", 0)):
            handler = CSVHandler()
    
    assert CSVHandler.dict_of_rules == {}


def test_save_rules_success():

    CSVHandler.dict_of_rules = {"Wycieczki/Hotel": ["BOOKING", "PARKHOTEL"]}
    
    with patch("builtins.open", mock_open()) as mocked_file:
        with patch("json.dump") as mocked_json_dump:
            handler = CSVHandler()
            handler.save_rules()

            mocked_file.assert_called_once_with('rules_dict.json', 'w')
            mocked_json_dump.assert_called_once_with(CSVHandler.dict_of_rules, mocked_file)


def test_save_rules_ioerror():

    CSVHandler.dict_of_rules = {"Wycieczki/Hotel": ["BOOKING", "PARKHOTEL"]}
    with patch("builtins.open", mock_open()) as mocked_file:
        mocked_file.side_effect = IOError("Unable to write to file")

        handler = CSVHandler()

        with patch("logging.error") as mock_log_error:
            handler.save_rules()

            mock_log_error.assert_called_once_with("File I/O error: Unable to write to file")

def test_load_csv_isnone():

    handler = CSVHandler(df=None)

    with patch("logging.error") as mock_log_error:
        with pytest.raises(ValueError, match='DataFrame is not set'):
            handler.load_csv()

            mock_log_error.assert_called_once_with('No DataFrame available to load')



def load_csv_success():

    mock_df = pd.DataFrame({"Transakcja": ["Kupa"], "Cena": [100]})

    handler = CSVHandler(df=mock_df)
    
    with patch("logging.info") as mock_log_info:
        returned_df = handler.load_csv()
        assert mock_df.equals(returned_df)

        mock_log_info.assert_called_once_with("CSV dataframe loaded successfully")

