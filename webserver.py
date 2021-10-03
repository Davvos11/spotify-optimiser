from flask import Flask
import flask
from threading import Thread
from queue import Queue
from time import sleep


class Server:
    def __init__(self):
        self.queue = Queue()
        self.app = self._create_flask()
        Thread(target=self.app.run).start()

    def _create_flask(self):
        app = Flask(__name__)

        @app.route('/')
        def hello_world():
            return flask.render_template('index.html')

        @app.route('/stream')
        def streamed_response():
            @flask.stream_with_context
            def generate():
                while True:
                    yield "data: "+self.queue.get()+"\n\n"
            return flask.Response(generate(), mimetype='text/event-stream')

        return app
