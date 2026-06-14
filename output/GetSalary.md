# Procedure: GetSalary

## Purpose
The `GetSalary` procedure is designed to retrieve the salary information for all employees currently stored in the `Employees` table.

## Inputs
This procedure does not require any input parameters.

## Outputs
The procedure returns a result set containing the following column:
*   `Salary` (datatype inferred from table schema, typically numeric or money)

## Side Effects
This procedure performs a read-only `SELECT` operation on the `Employees` table. It does not modify any data in the database, nor does it have any other observable side effects. It does not initiate or manage any transactions.

## Error Handling
This procedure does not include any explicit error handling mechanisms. In case of a database error (e.g., table not found, permissions issue), the error would propagate to the caller.

## Sample Call

```sql
EXEC GetSalary;
```