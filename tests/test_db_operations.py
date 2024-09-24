import pytest
from fastapi.testclient import TestClient
from app.main import app
from io import StringIO
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session



client = TestClient(app)
SAMPLE_CSV_CONTENT = """
id;date;receiver;title;amount;transaction_type;category;ref_number;exec_month
1;2024-08-29;ZABKA Z7582 K.1 WROCLAW;********3066106;-6.99;TRANSAKCJA KARTĄ PŁATNICZĄ;Artykuły spożywcze;'C992424207703228';2024-08
2;2024-08-29;BIEDRONKA 1234;********1234567;-10.50;TRANSAKCJA KARTĄ PŁATNICZĄ;Artykuły spożywcze;'B123456789012345';2024-08
3;2024-08-28;PETROL STATION ABC;BLIK REF 9876543210;50.00;PŁATNOŚĆ BLIK;Bez kategorii;'P987654321098765';2024-08
4;2024-08-27;SUPERMARKET XYZ;********9876543;-20.00;TRANSAKCJA KARTĄ PŁATNICZĄ;Artykuły spożywcze;'S987654321098765';2024-08
"""


@pytest.fixture
def mock_db_session(mocker):
    """
    Fixture to mock the database session.
    """

    #Create mock session object with the same spec as SQLalchemy's Session
    mock_session = MagicMock(spec=Session)
    #Patch the get_sql_db dependency to return the mock session
    mocker.patch('main.get_sql_db', return_value=mock_db_session)
    return mock_session


@pytest.fixture
def mock_transaction_service(mocker):
    """
    Fixture to mock the Transaction service class.
    """

    mock_service_instance = MagicMock()
    mocker.patch('main.TransactionService', return_value=mock_service_instance)
    return mock_service_instance


def mock_csv_handler(mocker):
    """
    Fixture to mock the CSV handler class and it's methods.
    """

    mock_handler_instance = MagicMock()
    mocker.patch('main.CSVHandler', return_value=mock_handler_instance)

    mock_handler_instance.load_csv.return_value = MagicMock()
    mock_handler_instance.create_df_for_db.return_value = MagicMock()
    mock_handler_instance.rename_columns.return_value = MagicMock()

    return mock_handler_instance


def test_db_operations_add_transactions_valid_CSV(mocker, mock_db_session, mock_transaction_service, mock_csv_handler):

    csv_file = StringIO(SAMPLE_CSV_CONTENT)
    files = {
        'file': ('test.csv', csv_file, 'text/csv')
    }

    expected_records = 4
    mock_new_df = mock_csv_handler.rename_columns.return_value
    mock_new_df.to_dict.return_value

    
    mock_new_df = mock_csv_handler.rename_columns.return_value
    mock_new_df.to_dict.return_value = {
        0: {'id': 1, 'date': '2024-08-29', 'receiver': 'ZABKA Z7582', 'amount': -6.99},
        1: {'id': 2, 'date': '2024-08-29', 'receiver': 'BIEDRONKA 1234', 'amount': -10.50},
        2: {'id': 3, 'date': '2024-08-28', 'receiver': 'PETROL STATION', 'amount': 50.00},
        3: {'id': 4, 'date': '2024-08-27', 'receiver': 'SUPERMARKET XYZ', 'amount': -20.00}
    }

    response = client.post("/transactions/add_csv", files=files)
    
    assert response.status_code == 201, f"Expected status code 201, got {response.status_code}"
    response_json = response.json()
    assert response_json["status"] == "success", f"Exepcted status 'success', got {response_json['status']}"
    assert response_json["records_processed"] == expected_records, (f"Expected records_processed {expected_records}, got {response_json["records_processed"]}")

    mock_csv_handler.load_csv.assert_called_once()
    mock_csv_handler.create_df_for_db.assert_called_once()
    mock_csv_handler.rename_columns.assert_called_once()

    app.main.TransactionService.assert_called_once_with(mock_db_session)
    mock_transaction_service.add_transactions.assert_called_once()

    #Optionally, verify the arguments passed to add_transactions
    args, kwargs = mock_transaction_service.add_transactions.call_args
    assert args[0] == 'models.Transaction'
    assert len(args[1]) == expected_records
    


def test_get_timeline():

    test_output = [
    "2024-07",
    "2024-06",
    "2024-08"
]

    response = client.get('/transactions/get_timeline')
    assert response.status_code == 200
    assert response.json() == test_output


def test_get_summary():

    response = client.get('/transactions/get_summary')
    assert response.status_code == 200

    response_data = response.json()

    assert 'income' in response_data
    assert 'expenses' in response_data

    assert isinstance(response_data['income'], float)
    assert isinstance(response_data['expenses'], float)

    print (f" Income is :{response_data['income']} Expenses is: {response_data['expenses']}")



