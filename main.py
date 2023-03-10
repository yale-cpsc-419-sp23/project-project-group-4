from website import create_app
import argparse

app = create_app()

def parse():
    """
    uses the python argparse library to assign arguments
    """
    parser = argparse.ArgumentParser(description='Client for the YUAG application', allow_abbrev=False)
    parser.add_argument('--port', type=int, default=5000, help=
        'the port at which to run the website')

    args = parser.parse_args()

    return args

if __name__ == '__main__':
    args = parse()
    app.run(host='127.0.0.1', port = args.port, debug=True)