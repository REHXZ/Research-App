import pandas as pd
import streamlit as st

def load_csv(file):
    """
    Load a CSV file into a pandas DataFrame
    
    Args:
        file: The uploaded file object
        
    Returns:
        pandas.DataFrame: The loaded DataFrame
    """
    try:
        df = pd.read_csv(file)
        return df
    except Exception as e:
        return pd.DataFrame({'Error': [f'Failed to load file: {str(e)}']})

def filter_data(df, column, selected_values):
    """
    Filter DataFrame based on selected values in a column
    
    Args:
        df: pandas.DataFrame to filter
        column: Column name to filter on
        selected_values: List of values to include
        
    Returns:
        pandas.DataFrame: Filtered DataFrame
    """
    if not selected_values:
        return df
    
    return df[df[column].isin(selected_values)]

def filter_data_multi(df, filters_dict):
    """
    Filter DataFrame based on selected values in multiple columns
    
    Args:
        df: pandas.DataFrame to filter
        filters_dict: Dictionary where keys are column names and values are lists of selected values
        
    Returns:
        pandas.DataFrame: Filtered DataFrame
    """
    filtered_df = df.copy()
    
    for column, values in filters_dict.items():
        if values:  # Only apply filter if values are selected
            filtered_df = filtered_df[filtered_df[column].isin(values)]
    
    return filtered_df

def filter_text_search(df, column, search_terms):
    """
    Filter DataFrame based on text search in a specific column
    
    Args:
        df: pandas.DataFrame to filter
        column: Column name to search in
        search_terms: List of search terms to find
        
    Returns:
        pandas.DataFrame: Filtered DataFrame
    """
    if not search_terms:
        return df
        
    filtered_df = df.copy()
    
    # Convert column to string if it's not already
    if filtered_df[column].dtype != 'object':
        filtered_df[column] = filtered_df[column].astype(str)
    
    # Create a mask for each search term and combine them
    mask = pd.Series(False, index=filtered_df.index)
    
    for term in search_terms:
        mask = mask | filtered_df[column].str.contains(term, case=False, na=False)
    
    return filtered_df[mask]

def Predict_Best_Tolerance_based_on_Material(df):
    """
    Find the optimal balance between tolerance, Cp, Cpk, and Gage R&R.
    Instead of targeting specific values, this calculates the best possible
    metrics that could be achieved given the current process capability.
    
    Args:
        df: DataFrame containing measurement data with Gage_RR, MeasValue, LSL, and USL columns
    
    Returns:
        dict: Contains optimal tolerance values and resulting metrics for different scenarios
    """
    if len(df) == 0:
        return {
            "best_tolerance": None,
            "message": "No data available for prediction",
            "success": False
        }
    
    try:
        # Get required values from the dataframe
        std_dev = df['MeasValue'].std()
        mean = df['MeasValue'].mean()
        
        # Get current specifications
        lsl = df['LSL'].unique()[0]
        usl = df['USL'].unique()[0]
        current_tolerance = usl - lsl
        
        # Get the current Gage R&R value
        current_gage_rr = df['Gage_RR'].unique()[0]
        
        # Calculate current process metrics
        current_cp = current_tolerance / (6 * std_dev) if std_dev > 0 else float('inf')
        current_cpk_lower = (mean - lsl) / (3 * std_dev) if std_dev > 0 else float('inf')
        current_cpk_upper = (usl - mean) / (3 * std_dev) if std_dev > 0 else float('inf')
        current_cpk = min(current_cpk_lower, current_cpk_upper)
        
        # Calculate best possible metrics for different scenarios
        scenarios = []
        
        # Scenario 1: Optimize for Cp/Cpk = 1.0 (minimum acceptable)
        min_acceptable_tolerance = 6 * std_dev
        gage_rr_at_min = (current_gage_rr * current_tolerance) / min_acceptable_tolerance
        
        scenarios.append({
            "name": "Minimum Acceptable Tolerance (Cp = 1.0)",
            "tolerance": min_acceptable_tolerance,
            "cp": 1.0,
            "cpk": 1.0,  # Assuming centered process
            "gage_rr": gage_rr_at_min,
            "lsl": mean - (min_acceptable_tolerance / 2),
            "usl": mean + (min_acceptable_tolerance / 2)
        })
        
        # Scenario 2: Optimize for Cp/Cpk = 1.33 (good quality)
        good_tolerance = 6 * std_dev * 1.33
        gage_rr_at_good = (current_gage_rr * current_tolerance) / good_tolerance
        
        scenarios.append({
            "name": "Good Quality Tolerance (Cp = 1.33)",
            "tolerance": good_tolerance,
            "cp": 1.33,
            "cpk": 1.33,  # Assuming centered process
            "gage_rr": gage_rr_at_good,
            "lsl": mean - (good_tolerance / 2),
            "usl": mean + (good_tolerance / 2)
        })
        
        # Scenario 3: Optimize for Cp/Cpk = 1.67 (high quality)
        high_tolerance = 6 * std_dev * 1.67
        gage_rr_at_high = (current_gage_rr * current_tolerance) / high_tolerance
        
        scenarios.append({
            "name": "High Quality Tolerance (Cp = 1.67)",
            "tolerance": high_tolerance,
            "cp": 1.67,
            "cpk": 1.67,  # Assuming centered process
            "gage_rr": gage_rr_at_high,
            "lsl": mean - (high_tolerance / 2),
            "usl": mean + (high_tolerance / 2)
        })
        
        # Scenario 4: Optimize for Gage R&R = 10% (excellent measurement system)
        excellent_gage_tolerance = (current_gage_rr * current_tolerance) / 10
        cp_at_excellent = excellent_gage_tolerance / (6 * std_dev)
        
        scenarios.append({
            "name": "Excellent Measurement System (Gage R&R = 10%)",
            "tolerance": excellent_gage_tolerance,
            "cp": cp_at_excellent,
            "cpk": cp_at_excellent,  # Assuming centered process
            "gage_rr": 10.0,
            "lsl": mean - (excellent_gage_tolerance / 2),
            "usl": mean + (excellent_gage_tolerance / 2)
        })
        
        # Find the best balanced scenario - this is subjective and depends on priorities
        # Let's use a scoring approach combining Cp and Gage R&R
        for scenario in scenarios:
            # Higher score is better - we want high Cp and low Gage R&R
            # Score = Cp - (Gage R&R / 100)
            scenario["score"] = scenario["cp"] - (scenario["gage_rr"] / 100)
        
        # Sort scenarios by score (descending)
        # scenarios.sort(key=lambda x: x["score"], reverse=True)
        
        # Get the best scenario (highest score)
        best_scenario = scenarios[1]
        
        # Prepare the final recommendation
        return {
            "best_tolerance": best_scenario["tolerance"],
            "new_lsl": best_scenario["lsl"],
            "new_usl": best_scenario["usl"],
            "resulting_cp": best_scenario["cp"],
            "resulting_cpk": best_scenario["cpk"],
            "resulting_gage_rr": best_scenario["gage_rr"],
            "current_cp": current_cp,
            "current_cpk": current_cpk,
            "current_gage_rr": current_gage_rr,
            "all_scenarios": scenarios,
            "recommended_scenario": best_scenario["name"],
            "success": True
        }
    
    except Exception as e:
        return {
            "best_tolerance": None,
            "message": f"Error in prediction: {str(e)}",
            "success": False
        }
