from pairamid_api.extensions import socketio
from . import operations

@socketio.on('add pair')
def create(json, methods=['GET', 'POST']):
    new_pair = operations.run_create()
    socketio.emit('add pair', new_pair)
    return True

@socketio.on('delete pair')
def delete(json, methods=['GET', 'POST']):
    uuid = operations.run_delete(json['uuid'])
    socketio.emit('delete pair', uuid)
    return  True

@socketio.on('batch update pairs')
def batch_update(json,methods=['GET', 'POST']):
    pairs = operations.run_batch_update(json)
    socketio.emit('batch update pairs', pairs)
    return  True

@socketio.on_error_default
def default_error_handler(e):
    print('\n\n {e} \n\n')
    return {'error': True, 'message': str(e) }