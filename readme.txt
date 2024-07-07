#DB details
DB name: HomeBudget_db -> Postgresql
Sensitive DB data stored in environemntal variable: DB_URL="postgresql://sylwestersojka:123@localhost/homebudget_db"    

db creation command:
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    receiver VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    category VARCHAR(100) NOT NULL
);
