"""
    Script which prepends the desired prefix(which is passed to the script using the --prepend_with arg 
    to all values in the columns col_one and col_two. Which by default are set to Ref_Wave and Test_Wave.
    
    It will only prepend the prefix if the value doesn't already start with it. 

    The csv dataset loaded and prefixed is then written back to the orignal csv file or to the desired output path
    if the argument --out_file is passed.
"""

# /usr/bin/env python3.8

import pandas as pd
import argparse
import sys

def main():
    try:
        args = init_argparser().parse_args()
        df = pd.read_csv(args.dataset)
        ref_col = args.col_one
        test_col = args.col_two

        ref_mask = ~df[ref_col].str.startswith(args.prepend_with, na=False)
        test_mask = ~df[test_col].str.startswith(args.prepend_with, na=False)

        df[ref_col].mask(ref_mask, args.prepend_with + df[ref_col], inplace=True)
        df[test_col].mask(test_mask, args.prepend_with + df[test_col], inplace=True)

        print(f'Prepended columns with {args.prepend_with}')
        if args.out_file:
            df.to_csv(args.out_file, index=False)
        else:
            df.to_csv(args.dataset, index=False)
        return 
    except Exception as err:
        print(err)
        sys.exit(1)

def init_argparser() -> argparse.ArgumentParser:
    """Initialize an argument parser with all of the possible command line arguments that can be passed to this script.

    Returns
    -------
    parser: argparse.ArgumentParser
        Parser to be used to parse arguments
    """
    parser = argparse.ArgumentParser(usage="%(prog)s", description="prepend_files")
    required = parser.add_argument_group('Required Arguments')
    required.add_argument('--dataset', required=True)
    required.add_argument('--prepend_with', required=True)
    optional = parser.add_argument_group('Optional Arguments')
    optional.add_argument('--out_file')
    optional.add_argument('--col_one', default='Ref_Wave')
    optional.add_argument('--col_two', default='Test_Wave')
    return parser


if __name__ == '__main__':
    main()