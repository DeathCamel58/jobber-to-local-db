import math

from rich.console import Console
from rich.layout import Layout
from rich import print
from rich.pretty import pprint

import getter


if __name__ == '__main__':
    # Initialize rich console UI
    console = Console()
    layout = Layout

    # Get all data from Jobber
    getter.get_data()

