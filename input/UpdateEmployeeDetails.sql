CREATE PROCEDURE UpdateEmployeeDetails
    @EmployeeId INT,
    @Email VARCHAR(100),
    @DepartmentId INT,
    @Salary DECIMAL(10,2)
AS
BEGIN
    UPDATE Employees
    SET 
        Email = @Email,
        DepartmentId = @DepartmentId,
        Salary = @Salary
    WHERE EmployeeId = @EmployeeId

    IF @@ROWCOUNT = 0
        PRINT 'No employee found with given ID'
    ELSE
        PRINT 'Employee updated successfully'
END
