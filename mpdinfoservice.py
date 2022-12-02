import os
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket import WebSocketError
from mpd import MPDClient
from io import BytesIO
from PIL import Image
import json
import time
from bottle import request, Bottle, abort, response, template
from gevent import monkey
monkey.patch_all()


app = Bottle()

# where is the mpd host 
mpd_host= os.environ.get('MPD_HOST' , 'localhost')
# where is the musik
mpd_root_dir = os.environ.get('MPD_ROOT_DIR' , '/data/Musik/')
# where the websocket should connect to
listen_on = os.environ.get('LISTEN_ON' , '127.0.0.1')

ws_port = os.environ.get('PORT' , 9999)

print (f"MPD Host: {mpd_host} , I listen on {listen_on}:{ws_port}. music dir is {mpd_root_dir}")




@app.route('/')
def start_page():
    """ Returns the start html page """
    return template('start_page_template', listen_on=listen_on , ws_port=ws_port)



@app.route('/img')
def img():
    """Returns the image of the current song or stream"""
    client = MPDClient()
    client.connect(host=mpd_host, port=6600)
    client.command_list_ok_begin()
    client.currentsong()
    result = client.command_list_end()
    if not result[0]:
        result.append([])
    file = result[0].get('file', 'none')
    found=False 
    if file == 'none':
        image = Image.open('streams/idle.jpeg')
    elif file.startswith('http://'):
        # Streams
        filepath = file.replace('/', '|')
        try:
            image = Image.open('streams/' + filepath)
            found=True 
        except ('FileNotFoundError'):
            image = Image.open('streams/default.jpeg')
    else:
        # Files 
        basename = os.path.dirname(file)
        filelist = ['cover.jpg', 'folder.jpg',
                    'cover.png', 'CD.jpg', 'Front.jpg' ,
                    'Cover.jpg' , 'Covers/Front.jpg' ,
                    'Folder.jpg' , 'front.jpeg' ,
                    'back.jpeg' , 'cd.jpeg' ,
                    'cover.jpeg'  , 'AlbumArtSmall.jpg' ,
                    'fanart.jpg' , 'front.jpg' ,
                    '.folder.png' , 'cover.1.png']
        image = Image.open('streams/default.jpeg')  # set a default
        for coverfile in filelist:
            cover = mpd_root_dir + '/' + basename + '/' + coverfile
            if not os.access(cover, os.R_OK):
                continue
            else:
                image = Image.open(cover)
                found =True
                break
    if not found:
        if result[0].get('album') and result[0].get('artist'): 
            # lets try get_cover.sh
            try:
                os.system('/usr/local/bin/get_cover.sh')
                # and again:
                found=True
                img()
            except Exception:
                sys.exec_clear()
    if not found:
        image = Image.open('streams/default.jpeg')
    image_buffer = BytesIO()
    image.save(image_buffer, format="jpeg")
    response.set_header('Content-type', 'image/jpeg')
    return image_buffer.getvalue()

        


@ app.route('/websocket')
def handle_websocket():
    """Sends new song/stream data to on the websocket """
    wsock = request.environ.get('wsgi.websocket')
    if not wsock:
        abort(400, 'Expected WebSocket request.')
    client = MPDClient()
    client.connect(host=mpd_host, port=6600)
    while True:
        client.command_list_ok_begin()
        client.currentsong()
        result = client.command_list_end()
        if not result[0]:
            result.append([])
        show_file = result[0].get('file', '')
        show_title = result[0].get('title', 'idle')
        if not result[0].get('track') :
            show_album = result[0].get('album', '')
        else :
            show_album = result[0].get('track' , '' ) + '. ' + result[0].get('album', '')
        show_name = result[0].get('name' , result[0].get('artist' , '')) 

        send_it = {'type': 'string',
                   'text': "<div style=\"font-size: 400%\">" + show_name
                   + '</div><br><div style=\"font-size:150%\">'
                   + show_title + '</div><br>'  + show_album
                   }
        wsock.send(json.dumps(send_it))
        send_it = {'type': 'pict'}
        wsock.send(json.dumps(send_it))
        client.idle()


server = WSGIServer(("0.0.0.0", ws_port), app,
                    handler_class=WebSocketHandler)
print (f"Started  Webserver on 0.0.0.0 {ws_port}") 
server.serve_forever()
