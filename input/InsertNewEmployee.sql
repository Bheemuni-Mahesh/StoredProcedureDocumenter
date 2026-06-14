CREATE PROCEDURE InsertNewEmployee
    @FirstName VARCHAR(50),
    @LastName VARCHAR(50),
    @Email VARCHAR(100),
    @DepartmentId INT,
    @DateOfJoining DATE,
    @Salary DECIMAL(10,2)
AS
BEGIN
    INSERT INTO Employees (FirstName, LastName, Email, DepartmentId, DateOfJoining, Salary)
    VALUES (@FirstName, @LastName, @Email, @DepartmentId, @DateOfJoining, @Salary)

    PRINT 'Employee inserted successfully'
END
