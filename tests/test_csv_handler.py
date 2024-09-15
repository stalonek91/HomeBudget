import pandas as pd
import json
import pytest
from unittest.mock import mock_open, patch, call

from app.csv_handler import CSVHandler

@pytest.fixture(autouse=True)
def reset_dict_of_rules():
    CSVHandler.dict_of_rules = {}

@pytest.fixture
def test_df():
    data = {
        'Data księgowania': ["2024-01-01", "2024-01-02", "2024-01-03"],
        'Nadawca / Odbiorca': ["Alice", "Bob", "Charlie"],
        'Tytułem': ["Payment", "Invoice", "Refund"],
        'Kwota operacji': [100.50, -20.00, 35.75],
        'Typ operacji': ["credit", "debit", "credit"],
        'Kategoria': ["Food", "Rent", "Utilities"],
        'Numer referencyjny': ["TXN001", "TXN002", "TXN003"]
    }
    return pd.DataFrame(data)

@pytest.fixture
def test_df_with_nok():
    data = {
        'Data ksi111ęgowania': ["2024-01-01", "2024-01-02", "2024-01-03"],
        'Nadawca / Odbiorca': ["Alice", "Bob", "Charlie"],
        'Tytułem': ["Payment", "Invoice", "Refund"],
        'Kwota operacji': [100.50, -20.00, 35.75],
        'Typ operacji': ["credit", "debit", "credit"],
        'Kategoria': ["Food", "Rent", "Utilities"],
        'Numer referencyjny': ["TXN001", "TXN002", "TXN003"]
    }
    return pd.DataFrame(data)


@pytest.fixture
def test_df_with_additional_cols():
    data = {
        'Data księgowania': ["2024-01-01", "2024-01-02", "2024-01-03"],
        'Nadawca / Odbiorca': ["Alice", "Bob", "Charlie"],
        'Tytułem': ["Payment", "Invoice", "Refund"],
        'Kwota operacji': [100.50, -20.00, 35.75],
        'Typ operacji': ["credit", "debit", "credit"],
        'Kategoria': ["Food", "Rent", "Utilities"],
        'Numer referencyjny': ["TXN001", "TXN002", "TXN003"],
        'Additional Column 1': ["Extra1", "Extra2", "Extra3"],
        'Random Data': [123, 456, 789],
        'Extra Column': ["X", "Y", "Z"],
        'Placeholder': [True, False, True],
        'Notes': ["Test note 1", "Test note 2", "Test note 3"]
    }
    return pd.DataFrame(data)


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
    
    with patch.object(CSVHandler, '_load_rules', return_value=None):
        with patch("builtins.open", mock_open()) as mocked_file:
            with patch("json.dump") as mocked_json_dump:
                handler = CSVHandler()
                handler.save_rules()

                mocked_file.assert_called_once_with('rules_dict.json', 'w')
                mocked_json_dump.assert_called_once_with(CSVHandler.dict_of_rules, mocked_file())


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



def test_load_csv_success():

    mock_df = pd.DataFrame({"Transakcja": ["Kupa"], "Cena": [100]})

    handler = CSVHandler(df=mock_df)
    
    with patch("logging.info") as mock_log_info:
        returned_df = handler.load_csv()
        assert mock_df.equals(returned_df)

        mock_log_info.assert_called_once_with("CSV dataframe loaded successfully")


def test_check_missing_columns_OK(test_df):

    handler = CSVHandler()
    handler._check_missing_columns(df=test_df, columns=CSVHandler.columns_to_keep)


def test_check_missing_columns_error(test_df_with_nok):


    with patch("logging.error") as mock_log_error:
        with pytest.raises(ValueError, match='Missing columns in Dataframe'):
            handler = CSVHandler()
            handler._check_missing_columns(df=test_df_with_nok, columns=CSVHandler.columns_to_keep)

            missing_columns = ['Data ksiegowania']
            mock_log_error.assert_called_once_with(f'Missing columns in Dataframe: {missing_columns}')


def test_create_df_for_db_ok(test_df_with_additional_cols, test_df):
    handler = CSVHandler()
    output_df = handler.create_df_for_db(base_df=test_df_with_additional_cols)

    assert output_df.equals(test_df)



def test_create_df_for_db_nok(test_df_with_nok):

    with patch("logging.error") as mocked_log_error:
        handler = CSVHandler()
        output_df = handler.create_df_for_db(base_df=test_df_with_nok)

        mocked_log_error.assert_has_calls([
            call("Missing columns in Dataframe: ['Data księgowania']"),  # First error log
            call("Error processing CSV: Missing columns in Dataframe")   # Second error log
        ])

        assert output_df is None



def test_rename_columns_missing_columns():

    data_with_missing_column = {
    'Data księgowania': ["2024-01-01", "2024-01-02", "2024-01-03"],
    'Nadawca / Odbiorca': ["Alice", "Bob", "Charlie"],
    'Tytułem': ["Payment", "Invoice", "Refund"],
    'Kwota operacji': [100.50, -20.00, 35.75],
    # 'Typ operacji' is intentionally missing
    'Kategoria': ["Food", "Rent", "Utilities"],
    'Numer referencyjny': ["TXN001", "TXN002", "TXN003"]
}
    
    df_with_missing_columns = pd.DataFrame(data_with_missing_column)

    handler = CSVHandler()

    with patch.object(handler, '_load_rules', return_value=None):
        with patch("logging.error") as mock_log_error:
            print("Columns in DataFrame:", df_with_missing_columns.columns)
            print("Columns in DataFrame:", handler.columns_to_keep)
            with pytest.raises(ValueError, match="Missing columns in Dataframe"):
                handler.rename_columns(df_with_missing_columns)

            mock_log_error.assert_called_once_with("Missing columns in Dataframe: ['Typ operacji']")


    
