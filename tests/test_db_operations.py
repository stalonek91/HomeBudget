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




def test_get_timeline():

    test_output = [
    "2024-07",
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


def test_db_operations_add_transactions_valid_CSV():
