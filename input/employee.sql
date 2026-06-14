CREATE PROCEDURE GetEmployee
    @EmployeeId INT
AS
BEGIN
    SELECT *
    FROM Employees
    WHERE EmployeeId = @EmployeeId
END