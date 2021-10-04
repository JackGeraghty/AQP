"""Module for handling the different draw options for nodes. Used when creating a .dot file respresentation of the pipeline."""

_DEFAULT_DRAW_OPTIONS = {'shape': 'box', 'style': 'filled'}
_DEFAULT_AQP_OPTIONS = {'fillcolor': '#ffffff'}
_DEFAULT_VISQOL_OPTIONS = {'fillcolor': '#56b3e9B3'}
_DEFAULT_PESQ_OPTIONS = {'fillcolor': '#009e74B3'}
_DEFAULT_WARP_Q_OPTIONS = {'fillcolor': '#d55c00B3'}

DRAW_OPTIONS = {
        "AQP": _DEFAULT_AQP_OPTIONS,
        "ViSQOL": _DEFAULT_VISQOL_OPTIONS,
        "PESQ": _DEFAULT_PESQ_OPTIONS,
        "WARP-Q": _DEFAULT_WARP_Q_OPTIONS
    }

def create_full_options(default_options: dict=_DEFAULT_DRAW_OPTIONS,
                        other_options: dict=None):
    """Merge the default options and other options to create the full dict of draw options.
    
    Merges the draw options dict passed from JSON with the default options for 
    a particular node type.

    Parameters
    ----------
    default_options : dict, optional
        The default options unique for a particular node type to be used.
        The default is _DEFAULT_DRAW_OPTIONS.
    other_options : dict, optional
        Any other draw options passed from JSON. The default is None.

    Returns
    -------
    draw_options: dict
        Merged dict from the two dictionaries passed to the function.

    """
    if other_options is None:
        other_options = {}
    return {**_DEFAULT_DRAW_OPTIONS, **default_options, **other_options}


