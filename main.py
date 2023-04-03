from website.app import app
import argparse

def parse():
    """
    uses the python argparse library to assign arguments
    """
    parser = argparse.ArgumentParser(description='Argument for Port Number', allow_abbrev=False)
    parser.add_argument('--port', type=int, default=5000, help='the port at which to run the website')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse()
    app.run(host="0.0.0.0", port=args.port, debug=True, threaded=True, ssl_context=('cert.pem', 'key.pem'))
