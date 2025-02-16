import os
from webapp import app    # Imports the code from 

if __name__ == '__main__':
    HOST = os.environ.get('SERVER_HOST', 'localhost')

    try:
        PORT = int(os.environ.get('SERVER_PORT', '1000'))
    except ValueError:
        PORT = 1000

    app.run(HOST, PORT, debug=True)