from argparse import ArgumentParser

_parser = ArgumentParser(description='Type of run for the actual task')
_parser.add_argument('--task-type',
                     '-tt',
                     type=str,
                     help='Choose between Fastest Path or Exploration run',
                     choices=['fp', 'exp'],
                     default='fp',
                     required=True)


def get_parser():
    return _parser.parse_args()
