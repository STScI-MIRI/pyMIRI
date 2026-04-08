import logging
import pandas as pd
from pathlib import Path
from .fits_utils import get_fits_header_value

logger = logging.getLogger(__name__)

def add_fits_header_to_csv(csv_input, keyword, column_name='Filename'):
    """
    Reads a CSV, extracts a FITS header value for every row, 
    and adds it as a new column named after the keyword.
    """
    input_path = Path(csv_input).resolve()
    df = pd.read_csv(input_path)

    if column_name not in df.columns:
        raise KeyError(f"Column '{column_name}' missing from {input_path.name}")

    logger.info(f"Extracting {keyword} from files in column '{column_name}'...")
    
    # Use the modular utility to fill the new column
    df[keyword] = df[column_name].apply(lambda x: get_fits_header_value(x, keyword))
    
    return df

def filter_csv(df, filter_column, threshold, condition='gt'):
    """
    Filters a DataFrame based on a user-defined mathematical condition.
    
    Args:
        df (pd.DataFrame): The dataframe to filter.
        filter_column (str): The column to check.
        threshold (numeric): The value to compare against.
        condition (str): 'gt' (>), 'lt' (<), 'eq' (==), 'ge' (>=), 'le' (<=)
    """
    if filter_column not in df.columns:
        raise KeyError(f"Column '{filter_column}' not found in the DataFrame.")

    operators = {
        'gt': df[filter_column] > threshold,
        'lt': df[filter_column] < threshold,
        'eq': df[filter_column] == threshold,
        'ge': df[filter_column] >= threshold,
        'le': df[filter_column] <= threshold
    }
    
    if condition not in operators:
        raise ValueError(f"Condition '{condition}' not recognized. Use 'gt', 'lt', 'eq', 'ge', or 'le'.")

    filtered_df = df[operators[condition]].copy()
    logger.info(f"Filtered rows: {len(df)} -> {len(filtered_df)}")
    
    return filtered_df