CREATE PROCEDURE GetAllDepartments
AS
BEGIN
    SELECT 
        DepartmentId,
        DepartmentName,
        ManagerId,
        CreatedDate
    FROM Departments
    ORDER BY DepartmentName ASC
END
