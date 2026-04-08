import logging
from pathlib import Path
from astropy.io import fits

logger = logging.getLogger(__name__)

def get_fits_header_value(fits_path_str, keyword):
    """
    Retrieves a specific header value from a FITS file.
    
    Args:
        fits_path_str (str): Path to the FITS file.
        keyword (str): The header keyword to retrieve (e.g., 'NGROUPS').
        
    Returns:
        The value of the keyword, or None if not found/error.
    """
    fits_path = Path(fits_path_str)
    
    if not fits_path.exists():
        logger.error(f"FITS file not found: {fits_path}")
        raise FileNotFoundError(f"The FITS file {fits_path} does not exist.")
        
    try:
        with fits.open(fits_path) as hdul:
            # Check Primary header (index 0)
            val = hdul[0].header.get(keyword)
            # If not in Primary, check first extension (index 1)
            if val is None and len(hdul) > 1:
                val = hdul[1].header.get(keyword)
            return val
    except Exception as e:
        logger.warning(f"Could not read {keyword} from {fits_path}: {e}")
        return None