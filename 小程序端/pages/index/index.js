var img_text = "";

//注册页面
Page({
  data: {
    captchaImagec: '',
    src: "",
  },

  //选择图片
  chooseImage: function () {
    var that = this
    wx.chooseImage({
      count: 1,
      sizeType: ['original', 'compressed'],
      sourceType: ['album', 'camera'],
      success: function (res) {
        let src = res.tempFilePaths[0]
        that.setData({
          src: src
        })
      }
    })
  },

  //上传图片
  uploadFile: function () {
    var that = this
    let src = this.data.src
    if (src == '') {
      wx.showToast({
        title: '请选择文件！',
        icon: 'none'
      })
    } else {
      var uploadTask = wx.uploadFile({
        url: 'http://127.0.0.1:5000/',
        formData: { //HTTP 请求中其他额外的 form data 
          'name': src,
          'type': "photo"
        },
        filePath: src,
        name: 'file',
        success: function (res) {
          wx.showToast({
            title: '上传成功',
            icon: 'none'
          })
          console.log('上传成功')
          that.setData({
            result_text: img_text
          })
        }
      })
      uploadTask.onProgressUpdate((res) => {
        console.log('上传进度', res.progress)
        console.log('已经上传的数据长度', res.totalBytesSent)
        console.log('预期需要上传的数据总长度', res.totalBytesExpectedToSend)
      })
    }
  },

  //识别图片
  reg_image: function () {
    var that = this
    let src = this.data.src
    if (src == '') {
      wx.showToast({
        title: '请上传文件！',
        icon: 'none'
      })
    } else {
      wx.request({
        
        url: 'http://127.0.0.1:5000/reg',
        header: {
          'content-type': 'application/json' // 默认值
        },
        method: 'POST',
        success: res => {
          var data = res.data
          if (res.statusCode == 200) {
            console.log(res.data)
            this.setData({
              captchaImage: 'data:image/png;base64,' + data,  // data 为接口返回的base64字符串
            })
          }
        }
      })
    }
  },

})