# Procedure: GetEmployee

## Purpose
This stored procedure retrieves the details of a single employee from the `Employees` table based on their unique `EmployeeId`.

## Inputs
*   **@EmployeeId** (INT): The unique identifier of the employee whose details are to be retrieved.

## Outputs
The procedure does not have any explicit output parameters. It returns a result set containing all columns (`*`) from the `Employees` table for the employee matching the provided `@EmployeeId`.

## Side Effects
This procedure performs a `SELECT` operation and does not modify any data in the database. Therefore, it has no side effects on the database state.

## Error Handling
The procedure does not include any explicit error handling mechanisms (e.g., `TRY...CATCH` blocks).

## Sample Call
```sql
EXEC GetEmployee @EmployeeId = 101;
```