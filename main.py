"""Run the Kitsu tool. Pass your username as an argument (poetry run python main.py my_username)`."""

import sys

from kitsu_library_availability import app

if __name__ == '__main__':
    assert len(sys.argv) == 2, 'Expected username as CLI argument. Received: {}'.format(sys.argv[1:])
    app.run(username=sys.argv[1])
