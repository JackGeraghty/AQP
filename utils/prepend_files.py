import pandas as pd
import argparse

def main():
    args = init_argparser().parse_args()
    df = pd.read_csv(args.dataset)
    df['Ref_Wave'] = args.prepend_with + df['Ref_Wave'].astype(str)
    df['Test_Wave'] = args.prepend_with + df['Test_Wave'].astype(str)
    print(f'Prepended columns with {args.prepend_with}')
    if args.out_file:
        df.to_csv(args.out_file)
    else:
        df.to_csv(args.dataset)
    return


def init_argparser() -> argparse.ArgumentParser:
    """Initialize an argument parser with all of the possible command line arguments that can be passed to AQP.

    Returns
    -------
    parser: argparse.ArgumentParser
        Parser to be used to parse arguments
    """
    parser = argparse.ArgumentParser(usage="%(prog)s", description="AQP")
    required = parser.add_argument_group('Required Arguments')
    required.add_argument('--dataset', required=True)
    required.add_argument('--prepend_with', required=True)
    optional = parser.add_argument_group('Optional Arguments')
    optional.add_argument('--out_file')
    return parser


if __name__ == '__main__':
    main()
