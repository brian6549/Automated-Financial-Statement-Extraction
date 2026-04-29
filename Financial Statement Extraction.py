import pandas as pd
import requests


def get_sec_company_facts(ticker):
    """
    Gets the raw XBRL company facts JSON from the SEC EDGAR API for a given ticker.
    """
    
    # Initialize Headers
    # SEC Requirement: header needs to include name and contact info or else the request will get blocked
    headers = {
        'User-Agent': 'Brian Arias Cano brian.arias43@login.cuny.edu' 
    }

    print(f"Locating Central Index Key (CIK) for ticker: {ticker.upper()}...")
    
    # Get ticker from the SEC database
    mapping_url = "https://www.sec.gov/files/company_tickers.json"
    try:
        response = requests.get(mapping_url, headers=headers)
        response.raise_for_status()
        tickers_dict = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Network error getting SEC tickers: {e}")
        exit(1)

    # Get the CIK for the ticker if it exists
    cik_num = None
    for key, company in tickers_dict.items():
        if company['ticker'] == ticker.upper():
            cik_num = company['cik_str']
            break
            
    if not cik_num:
        print(f"Error: Could not find CIK for ticker '{ticker}'. Ensure the ticker is valid")
        exit(1) # Setup could be more graceful but it'll do

    # The SEC API requires the CIK to be exactly 10 digits, padded with leading zeros
    padded_cik = str(cik_num).zfill(10)
    print(f"Found CIK: {padded_cik}. getting financial facts...")

    # Get the Company Facts JSON. This contains the XBRL data
    facts_url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{padded_cik}.json"
    
    try:
        facts_response = requests.get(facts_url, headers=headers)
        facts_response.raise_for_status()
        company_facts = facts_response.json()
        
        print(f"Success. Downloaded raw XBRL data for {ticker.upper()}.")
        return company_facts
        
    except requests.exceptions.RequestException as e:
        print(f"Network Error getting company facts: {e}")
        exit(1)


def process_financial_data(raw_json):
    """
    Transforms raw SEC JSON into a pivoted Pandas DataFrame that mimics an income statement.
    """
    print("\nProcessing and standardizing financial data...")
    
    # The Standardization Dictionary
    # SEC filings use different tags for the same concept which can get chaotic. 
    # This dictionary maps as many XBRL tags as possible to standardized names.
    standard_metrics = {
        "Revenue": ["Revenues", "SalesRevenueNet", "SalesRevenueGoodsNet","RevenueFromContractWithCustomerExcludingAssessedTax", "TotalRevenuesAndOtherIncome"],
        "Cost of Goods Sold": ["CostOfGoodsAndServicesSold", "CostOfRevenue"],
        "Gross Profit": ["GrossProfit"],
        "Operating Income": ["OperatingIncomeLoss"],
        "Net Income": ["NetIncomeLoss"],
        "Total Assets": ["Assets"],
        "Total Liabilities": ["Liabilities"],
        "Total Equity": ["StockholdersEquity"]
    }

    # All of the relevant data is in the 'us-gaap' section of the JSON
    try:
        gaap_data = raw_json['facts']['us-gaap']
    except KeyError:
        print("Error: Could not find US-GAAP data in this filing.")
        return None
    
    # Initialize empty data set
    extracted_records = []

    # Extract and Filter the Data
    for clean_name, xbrl_tags in standard_metrics.items():
        for tag in xbrl_tags:
            if tag in gaap_data:
                # Only grabbing financial metrics that are in USD
                if 'USD' in gaap_data[tag]['units']:
                    data_points = gaap_data[tag]['units']['USD']
                    
                    for point in data_points:
                        # Only grabbing the annual data
                        # The SEC marks annual data with a 'form' of '10-K', some companies also file a 10-K/A in addiion. Checking both is necessary to find all of the correct XBRL tags
                        if point.get('form') in ['10-K','10K/A']:
                            extracted_records.append({
                                "Metric": clean_name,
                                "Year": point.get('fy'), # Fiscal Year
                                "Value": point.get('val')
                            })
                # This extraction process needs to go through all of the alternate tags because of how different they can be year to year and company to company

    # Build the Pandas DataFrame
    if not extracted_records:
        print("[!] No standard 10-K metrics could be extracted.")
        return None

    df = pd.DataFrame(extracted_records)

    # Clean Data Duplicates
    # If companies file both a 10-K and a 10-K/A, it can cause causing duplicate rows.
    # All duplicates are dropped, except the latest filing.
    df = df.drop_duplicates(subset=['Metric', 'Year'], keep='last')

    # Turn Years into columns, and Metrics into rows.
    pivoted_df = df.pivot(index='Metric', columns='Year', values='Value')
    
    # Mimic an actual income statement using the 'standard_metrics' dictionary as a template.
    ordered_index = [m for m in standard_metrics.keys() if m in pivoted_df.index]
    pivoted_df = pivoted_df.reindex(ordered_index)

    print("Standardization complete.")
    return pivoted_df

if __name__ == "__main__":
    
    target_ticker = input("Enter a stock ticker to get (e.g., AAPL, MSFT, JPM): ") 
    raw_data = get_sec_company_facts(target_ticker)

    # Just testing. this line outputs the entire JSON payload when uncommented
   # print(raw_data["facts"]) 

    if raw_data:
        clean_df = process_financial_data(raw_data)
        
        # Prints the last 5 years of data
        if clean_df is not None:
            # Divide by 1,000,000 to show values in millions for readability
            display_df = clean_df.iloc[:, -5:] / 1000000 
            print(f"\n--- {target_ticker.upper()} Financials (in Millions) ---")
            print(display_df.to_string(float_format="{:,.0f}".format))

        # Turn the the table into a CSV file.

        filename = f"{target_ticker.upper()}_financials.csv"
        clean_df.to_csv(filename)
        print(f"\n[*] Automation complete. File saved as {filename}")
        

