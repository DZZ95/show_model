# coding:utf-8
from flask import Flask, request
import base64
import gol
import tensorflow as tf
from preprocessing import preprocessing_factory
import reader
import model
import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'
gol._init()  # 先必须在主模块初始化（只在Main模块需要一次即可）
gol.set_value('upload_img_path', "")
upload_img_path = gol.get_value('upload_img_path')
def img(image_file = 'img/test.jpg',loss_model = 'vgg_16', image_size = 256, model_file = 'models/wave.ckpt-done'):

    height = 0
    width = 0
    with open(image_file, 'rb') as img:
        with tf.Session().as_default() as sess:
            if image_file.lower().endswith('png'):
                image = sess.run(tf.image.decode_png(img.read()))
            else:
                image = sess.run(tf.image.decode_jpeg(img.read()))
            height = image.shape[0]
            width = image.shape[1]
    # tf.logging.info('Image size: %dx%d' % (width, height))
    with tf.Graph().as_default():
        with tf.Session().as_default() as sess:
            # Read image data.
            image_preprocessing_fn, _ = preprocessing_factory.get_preprocessing(
                loss_model,
                is_training=False)
            image = reader.get_image(image_file, height, width, image_preprocessing_fn)
            # Add batch dimension
            image = tf.expand_dims(image, 0)
            generated = model.net(image, training=False)
            generated = tf.cast(generated, tf.uint8)
            # Remove batch dimension
            generated = tf.squeeze(generated, [0])
            # Restore model variables.
            saver = tf.train.Saver(tf.global_variables(), write_version=tf.train.SaverDef.V1)
            sess.run([tf.global_variables_initializer(), tf.local_variables_initializer()])
            # Use absolute path
            model_file = os.path.abspath(model_file)
            saver.restore(sess, model_file)
            # Make sure 'generated' directory exists.
            generated_file = 'generated/test3.jpg'
            if os.path.exists('generated') is False:
                os.makedirs('generated')
            # Generate and write image data to file.
            with open(generated_file, 'wb') as img:
                # start_time = time.time()
                img.write(sess.run(tf.image.encode_jpeg(generated)))
                # end_time = time.time()
                # tf.logging.info('Elapsed time: %fs' % (end_time - start_time))
                # tf.logging.info('Done. Please check %s.' % generated_file)

app = Flask(__name__)
@app.route('/', methods=['POST', 'GET'])
def upload():
    """接受前端传送来的文件"""
    f = request.files['file']
    if f is None:
        # 表示没有发送文件
        msg = "未上传文件"
        return msg

    img_name = request.form.get('name')
    str = img_name[-11:]  # 图片名称
    global upload_img_path
    upload_img_path = os.path.join('img/', str)  # 图片保存的路径
    f.save(upload_img_path)
    gol.set_value('upload_img_path', upload_img_path)
    return "json.dumps(result_text)"

@app.route('/reg', methods=['POST', 'GET'])
def reg():
    upload_img_path = gol.get_value('upload_img_path')
    img(image_file = upload_img_path)
    with open(r'./generated/test3.jpg', 'rb') as f:
        res = base64.b64encode(f.read())
        return res
    # return upload_img_path
if __name__ == '__main__':
    # 在本地端运行
    app.run(debug=True)

    # 部署的主机
    # app.run(host = '172.16.1.35', port = '5000', debug=True)

