from . import yolo
from . import yolov2
from . import vanilla
from os.path import basename

class framework(object):
    constructor = vanilla.constructor
    loss = vanilla.train.loss
    
    def __init__(self, meta, FLAGS):
        model = basename(meta['model'])
        model = '.'.join(model.split('.')[:-1])
        meta['name'] = model
        
        self.constructor(meta, FLAGS)

    def is_inp(self, file_name):
        return True

class YOLO(framework):
    constructor = yolo.constructor
    parse = yolo.data.parse
    shuffle = yolo.data.shuffle
    preprocess = yolo.predict.preprocess
    postprocess = yolo.predict.postprocess
    loss = yolo.train.loss
    is_inp = yolo.misc.is_inp
    profile = yolo.misc.profile
    _batch = yolo.data._batch
    resize_input = yolo.predict.resize_input
    findboxes = yolo.predict.findboxes
    process_box = yolo.predict.process_box
    get_json_box = yolo.predict.get_json_box

class YOLOv2(framework):
    constructor = yolo.constructor
    parse = yolo.data.parse
    shuffle = yolov2.data.shuffle
    preprocess = yolo.predict.preprocess
    loss = yolov2.train.loss
    is_inp = yolo.misc.is_inp
    postprocess = yolov2.predict.postprocess
    _batch = yolov2.data._batch
    resize_input = yolo.predict.resize_input
    findboxes = yolov2.predict.findboxes
    process_box = yolo.predict.process_box
    get_json_box = yolov2.predict.get_json_box

"""
framework factory
"""

types = {
    '[detection]': YOLO,
    '[region]': YOLOv2
}

def create_framework(meta, FLAGS):
    net_type = meta['type']
    this = types.get(net_type, framework)
    return this(meta, FLAGS)