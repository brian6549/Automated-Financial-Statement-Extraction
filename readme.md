

## Contact Information:
- Name: Brian Arias
- email: brian.arias43@login.cuny.edu

---

## 1. Project Title
> Automated Financial Statement Extraction & Standardization

---

## 2. Overview / Abstract
>   This project automates the retrieval, cleaning, and structuring of corporate financial data required for 3-statement financial modeling and valuation. Rather than manually navigating regulatory databases to compile historical financial metrics, this automation engine will programmatically fetch data directly from the SEC EDGAR system and standardize it.

>   This will cut out the maual labor of having to grab the data from the website so that an analyst can go straight to building financial models.

---

## 3. Task Description
### 3.1 Manual Process Description

Currently, when building a financial model, an analyst must:

1. Navigate to the SEC EDGAR website.

2. Search for a specific company using its ticker symbol.

3. Locate the most recent 10-K (Annual Report) or 10-Q (Quarterly Report).

4. Scroll through the document to find the Income Statement, Balance Sheet, and Cash Flow Statement.

5. Manually copy and paste historical data across multiple years into a spreadsheet.

6. Manually reformat the data to ensure columns align correctly and accounting terms are standardized.


### 3.2 Problem Statement

>   By nature The current process is tedious and prone to human error (like misaligning columns or dropping a zero). An analyst must interpret and standardize data row by row which takes time and brain power

### 3.3 Automation Goal

>   The goal is to automate the extraction and standardization pipeline. Successful automation means a user can input a single stock ticker, and the system will instantly output a formatted and standardized dataset of historical financial metrics ready for immediate use in a valuation model.

---

## 4. Inputs to the Task
> Describe all inputs required for the task.

### 4.1 Input Sources
> User Input: A string representing the target company's stock ticker (e.g., "AAPL").

> Web API: The SEC EDGAR REST API.

### 4.2 Input Formats
- The user input is plain text(the stock ticker)

### 4.3 Input Frequency
- Event-driven(input is entered when the user needs data)

---

## 5. Outputs and End States
> Describe the expected results of the automated process.

### 5.1 Outputs
- A clean, structured dataset containing key standardized financial metrics mapped across historical years.

### 5.2 Output Formats
- Final output is a CSV file containing the data

### 5.3 End State Conditions
>  The task is successfully completed when the script confirms the requested ticker data has been successfully parsed, standardized, and saved to the target directory or database.

---

## 6. Data Transformations
> Describe how data is processed and transformed throughout the task.

### 6.1 Transformation Steps
-   Extraction: Parse the JSON object to get specific XBRL accounting nodes.
-   Filtering/Validation: Filter out quarterly data to get strictly annual data points.
-   Standardization: Different organizations may use different words to describe revenue so we map those disparate tags to a standard dictionary(example: salesRevenue and Revenue can both be mapped to Revenue)
-   Pivoting: Transform the data shape from a vertical time-series list into a horizontal tabular format (Years as columns, Metrics as rows).


### 6.2 Transformation Examples
> Provide at least one concrete example:
- Input: {"taxonomy": "us-gaap", "tag": "SalesRevenueNet", "val": 394328000000, "fy": 2022, "fp": "FY"}
   
   Grab the fy and metric,(salesRevenueNet is already identified as a Revenue equivalent) and convert into a row and a column

---

## 7. Proposed Automation Approach

### 7.1 Techniques
- REST API interaction.

- JSON parsing and data wrangling.

- Dictionary mapping for standardization.

### 7.2 Tools and Technologies
- Programming languages: Python 3
- Libraries/frameworks: requests, pandas, json
- External services/APIs: SEC EDGAR Data API


---

## 8. Pseudocode for Automated Task

```
BEGIN

INITIALIZE SEC API headers (User-Agent string required by SEC)
DEFINE standardization_dictionary (maps raw XBRL tags to clean names)

PROMPT user for TARGET_TICKER

TRY:
    FETCH CIK (Central Index Key) for TARGET_TICKER from SEC mapping API
    FETCH Company Facts JSON from SEC EDGAR using CIK
CATCH HTTP_ERROR:
    PRINT "Failed to fetch data from SEC"
    EXIT

INITIALIZE empty dataset

FOR EACH accounting_concept IN standardization_dictionary DO
    IF concept EXISTS in Company Facts JSON THEN
        EXTRACT annual values and years
        CLEAN and scale numeric values
        APPEND to dataset with standardized name
    ELSE
        APPEND null values for concept
    END IF
END FOR

CONVERT dataset to tabular Pandas DataFrame
PIVOT DataFrame so Years are columns and Metrics are rows

EXPORT DataFrame to "TARGET_TICKER_financials.csv"

PRINT "Automation complete. File saved."

END

```

---

## 9. Testing and Validation Plan
> How will you verify that your automation works correctly?

- Test cases: Run the script against 3 different companies to ensure the standardization dictionary handles varying accounting structures.
- Expected vs. actual results: Manually download the 10-K for one company and verify the script's CSV output perfectly matches the printed numbers in the actual filing.
- Error handling strategies: try/except blocks to handle network timeouts, invalid ticker inputs, and SEC API rate-limiting rules


## 10. References

SEC EDGAR API Documentation: https://www.sec.gov/edgar/sec-api-documentation

Pandas Documentation: https://pandas.pydata.org/docs/

---
