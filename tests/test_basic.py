import re

def extract_procedure_name(sql_code):
    match = re.search(
        r'CREATE\s+PROCEDURE\s+(?:\[?dbo\]?\.\s*)?(?:\[)?(\w+)(?:\])?',
        sql_code,
        re.IGNORECASE
    )
    return match.group(1) if match else None

def test_read_sql_file():
    with open("input/employee.sql", "r") as f:
        content = f.read()
    assert "CREATE PROCEDURE" in content

def test_extract_procedure_name():
    sql = "CREATE PROCEDURE GetEmployee @EmployeeId INT AS BEGIN SELECT * FROM Employees END"
    name = extract_procedure_name(sql)
    assert name == "GetEmployee"