const storage = require('../../utils/storage');
const api = require('../../utils/api');

let idSeed = 0;

function makeId() {
  idSeed += 1;
  return 'm' + Date.now().toString(36) + idSeed.toString(36);
}

function chooseMedia(count) {
  return new Promise(function (resolve, reject) {
    wx.chooseMedia({
      count: count,
      mediaType: ['image'],
      sourceType: ['album', 'camera'],
      success: resolve,
      fail: reject
    });
  });
}

function requirePrivacy() {
  return new Promise(function (resolve) {
    if (typeof wx.requirePrivacyAuthorize !== 'function') {
      resolve();
      return;
    }
    try {
      wx.requirePrivacyAuthorize({
        success: resolve,
        fail: function () {
          // 让 chooseMedia 自己报错，下面的隐私错误处理会给出指引。
          resolve();
        }
      });
    } catch (error) {
      resolve();
    }
  });
}

function compressImage(path, quality, width, height) {
  return new Promise(function (resolve) {
    const options = {
      src: path,
      quality: quality,
      success: function (res) {
        resolve(res.tempFilePath || path);
      },
      fail: function () {
        resolve(path);
      }
    };
    if (width && height) {
      options.compressedWidth = width;
      options.compressedHeight = height;
    }
    wx.compressImage(options);
  });
}

function getImageInfo(path) {
  return new Promise(function (resolve) {
    wx.getImageInfo({
      src: path,
      success: resolve,
      fail: function () {
        resolve(null);
      }
    });
  });
}

function getFileInfo(path) {
  return new Promise(function (resolve, reject) {
    wx.getFileInfo({
      filePath: path,
      success: resolve,
      fail: reject
    });
  });
}

function readBase64(path) {
  return new Promise(function (resolve, reject) {
    wx.getFileSystemManager().readFile({
      filePath: path,
      encoding: 'base64',
      success: function (res) {
        resolve(res.data);
      },
      fail: reject
    });
  });
}

function mimeFromPath(path) {
  const match = /\.([a-zA-Z0-9]+)$/.exec(path || '');
  const ext = match ? match[1].toLowerCase() : '';
  if (ext === 'png') return 'image/png';
  if (ext === 'gif') return 'image/gif';
  if (ext === 'webp') return 'image/webp';
  return 'image/jpeg';
}

async function prepareImage(file) {
  let path = file.tempFilePath || file.path;
  let size = file.size || 0;

  const info = await getImageInfo(path);
  let targetWidth = 0;
  let targetHeight = 0;
  if (info && info.width && info.height) {
    const maxEdge = 1400;
    const longest = Math.max(info.width, info.height);
    const scale = longest > maxEdge ? maxEdge / longest : 1;
    targetWidth = Math.max(1, Math.round(info.width * scale));
    targetHeight = Math.max(1, Math.round(info.height * scale));
  }

  const qualities = [60, 40, 25];

  for (let index = 0; index < qualities.length; index += 1) {
    path = await compressImage(path, qualities[index], targetWidth, targetHeight);
    try {
      const fileInfo = await getFileInfo(path);
      size = fileInfo.size || size;
    } catch (error) {
      // 拿不到大小时继续，最后交给接口报错。
    }
    if (size && size <= 900 * 1024) break;
  }

  if (size > 2.5 * 1024 * 1024) {
    throw new Error('图片太大，请换一张');
  }

  const base64 = await readBase64(path);
  if (!base64) {
    throw new Error('读取图片失败');
  }
  return {
    id: makeId(),
    path: path,
    base64: base64,
    mime: mimeFromPath(path)
  };
}

function isCancel(error) {
  return !!(error && error.errMsg && error.errMsg.indexOf('cancel') >= 0);
}

function isPrivacyError(error) {
  const message = (error && (error.errMsg || error.message)) || '';
  return message.indexOf('privacy') >= 0 || message.indexOf('authorize') >= 0;
}

function showPrivacyHelp() {
  wx.showModal({
    title: '需要隐私授权',
    content: '请先在微信公众平台配置“用户隐私保护指引”（选中的照片/相机），再回来试一次。',
    showCancel: false
  });
}

Page({
  data: {
    messages: [],
    draft: '',
    pendingImages: [],
    sending: false,
    canSend: false,
    configured: false,
    modelLabel: '未配置',
    scrollInto: '',
    inputFocus: false,
    suggestions: [
      '这张图里写了什么？',
      '把图里的英文翻译成中文',
      '看看这道菜用了什么食材',
      '用三句话帮我总结这张截图'
    ]
  },

  settings: null,
  task: null,
  imageData: {},
  activeMessageId: '',
  activeText: '',
  deltaBuffer: '',
  flushTimer: null,

  onLoad() {
    this.imageData = {};
    this.reloadSettings(true);
  },

  onShow() {
    this.reloadSettings(false);
  },

  onUnload() {
    if (this.task && this.task.abort) this.task.abort();
    this.task = null;
    this.imageData = {};
    this.clearFlushTimer();
  },

  reloadSettings(showPrompt) {
    const settings = storage.loadSettings();
    this.settings = settings;
    const configured = !!(settings.baseURL && settings.model && settings.apiKey);
    this.setData({
      configured: configured,
      modelLabel: configured ? settings.model : '未配置'
    });

    if (showPrompt && !configured) {
      const that = this;
      wx.showModal({
        title: '先配置接口',
        content: '进入设置，填入 API Key 和模型后就能开始聊天。',
        confirmText: '去设置',
        cancelText: '稍后',
        success: function (res) {
          if (res.confirm) that.goSettings();
        }
      });
    }
  },

  goSettings() {
    wx.navigateTo({ url: '/pages/settings/settings' });
  },

  promptSettings() {
    const that = this;
    wx.showModal({
      title: '还差一步',
      content: '请先在设置里填写 API Key 和模型。',
      confirmText: '去设置',
      success: function (res) {
        if (res.confirm) that.goSettings();
      }
    });
  },

  newChat() {
    if (!this.data.messages.length) {
      wx.showToast({ title: '已经是新对话', icon: 'none' });
      return;
    }
    const that = this;
    wx.showModal({
      title: '新对话',
      content: '清空当前对话？',
      success: function (res) {
        if (!res.confirm) return;
        if (that.data.sending) that.stop();
        that.imageData = {};
        that.setData({
          messages: [],
          draft: '',
          pendingImages: [],
          canSend: false,
          scrollInto: ''
        });
      }
    });
  },

  onInput(event) {
    const draft = event.detail.value;
    this.setData({
      draft: draft,
      canSend: this.computeCanSend(draft, this.data.pendingImages)
    });
  },

  computeCanSend(draft, images) {
    return !!(String(draft || '').trim() || (images && images.length));
  },

  useSuggestion(event) {
    const text = event.currentTarget.dataset.text;
    this.setData({
      draft: text,
      canSend: true,
      inputFocus: true
    });
  },

  async chooseImages() {
    if (this.data.sending) return;
    const remaining = 3 - this.data.pendingImages.length;
    if (remaining <= 0) {
      wx.showToast({ title: '最多 3 张图片', icon: 'none' });
      return;
    }

    this.setData({ inputFocus: false });

    await requirePrivacy();

    let result = null;
    try {
      result = await chooseMedia(remaining);
    } catch (error) {
      if (isCancel(error)) return;
      if (isPrivacyError(error)) {
        showPrivacyHelp();
        return;
      }
      wx.showToast({ title: '选图失败', icon: 'none' });
      return;
    }

    const files = (result.tempFiles || []).slice(0, remaining);
    if (!files.length) return;

    wx.showLoading({ title: '处理图片…', mask: true });
    const prepared = [];

    try {
      for (let index = 0; index < files.length; index += 1) {
        prepared.push(await prepareImage(files[index]));
      }
      wx.hideLoading();

      const that = this;
      const displayImages = prepared.map(function (image) {
        that.imageData[image.id] = {
          base64: image.base64,
          mime: image.mime
        };
        return {
          id: image.id,
          path: image.path,
          mime: image.mime
        };
      });

      const pendingImages = this.data.pendingImages.concat(displayImages).slice(0, 3);
      this.setData({
        pendingImages: pendingImages,
        canSend: this.computeCanSend(this.data.draft, pendingImages)
      });
    } catch (error) {
      wx.hideLoading();
      if (isPrivacyError(error)) {
        showPrivacyHelp();
        return;
      }
      wx.showToast({
        title: (error && error.message) ? error.message : '图片处理失败',
        icon: 'none'
      });
    }
  },

  removeImage(event) {
    const index = Number(event.currentTarget.dataset.index);
    const pendingImages = this.data.pendingImages.slice();
    const removed = pendingImages.splice(index, 1)[0];
    if (removed && this.imageData[removed.id]) {
      delete this.imageData[removed.id];
    }
    this.setData({
      pendingImages: pendingImages,
      canSend: this.computeCanSend(this.data.draft, pendingImages)
    });
  },

  previewImage(event) {
    const src = event.currentTarget.dataset.src;
    if (!src) return;
    wx.previewImage({ current: src, urls: [src] });
  },

  send() {
    if (this.data.sending) return;
    if (!this.settings || !this.settings.apiKey || !this.settings.model) {
      this.promptSettings();
      return;
    }

    const text = (this.data.draft || '').trim();
    const pendingImages = this.data.pendingImages || [];
    if (!text && !pendingImages.length) return;

    const that = this;

    const userMessage = {
      id: makeId(),
      role: 'user',
      text: text,
      images: pendingImages.map(function (image) {
        return {
          id: image.id,
          path: image.path,
          mime: image.mime
        };
      }),
      waiting: false,
      error: false
    };

    const assistant = {
      id: makeId(),
      role: 'assistant',
      text: '',
      images: [],
      waiting: true,
      error: false
    };

    const history = this.data.messages
      .concat(userMessage)
      .filter(function (message) {
        return message.role === 'user' || (message.role === 'assistant' && message.text && !message.error);
      })
      .map(function (message) {
        return {
          role: message.role,
          text: message.text,
          error: !!message.error,
          images: (message.images || []).map(function (image) {
            const stored = that.imageData[image.id] || {};
            return {
              id: image.id,
              path: image.path,
              mime: stored.mime || image.mime,
              base64: stored.base64 || ''
            };
          }).filter(function (image) {
            return !!image.base64;
          })
        };
      });

    this.activeMessageId = assistant.id;
    this.activeText = '';
    this.deltaBuffer = '';
    this.setData({
      messages: this.data.messages.concat([userMessage, assistant]),
      draft: '',
      pendingImages: [],
      canSend: false,
      sending: true,
      inputFocus: false
    }, function () {
      that.scrollToBottom();
    });

    const settings = Object.assign({}, this.settings);

    try {
      this.task = api.streamChat({
        settings: settings,
        history: history,
        onDelta: function (delta) {
          that.queueDelta(delta);
        },
        onDone: function () {
          that.finishStream(false);
        },
        onError: function (message) {
          that.finishStream(true, message);
        }
      });
    } catch (error) {
      this.finishStream(true, (error && error.message) ? error.message : '请求失败');
    }
  },

  onSendOrStop() {
    if (this.data.sending) {
      this.stop();
    } else {
      this.send();
    }
  },

  stop() {
    if (!this.data.sending) return;
    if (this.task && this.task.abort) this.task.abort();
    this.task = null;
    this.clearFlushTimer();
    this.flushDelta();

    const index = this.findMessageIndex(this.activeMessageId);
    const text = this.activeText ? this.activeText + '\n\n（已停止）' : '（已停止）';
    const patch = { sending: false };
    if (index >= 0) {
      patch['messages[' + index + '].text'] = text;
      patch['messages[' + index + '].waiting'] = false;
      patch['messages[' + index + '].error'] = !this.activeText;
    }

    this.setData(patch, () => this.scrollToBottom());
    this.activeMessageId = '';
    this.activeText = '';
    this.deltaBuffer = '';
  },

  queueDelta(delta) {
    this.deltaBuffer += delta;
    if (this.flushTimer) return;
    const that = this;
    this.flushTimer = setTimeout(function () {
      that.flushDelta();
    }, 80);
  },

  flushDelta() {
    this.clearFlushTimer();
    const buffer = this.deltaBuffer;
    if (!buffer) return;
    this.deltaBuffer = '';
    this.activeText += buffer;

    const index = this.findMessageIndex(this.activeMessageId);
    if (index < 0) return;

    const patch = {};
    patch['messages[' + index + '].text'] = this.activeText;
    patch['messages[' + index + '].waiting'] = false;
    this.setData(patch);
    this.scrollToBottom();
  },

  clearFlushTimer() {
    if (this.flushTimer) {
      clearTimeout(this.flushTimer);
      this.flushTimer = null;
    }
  },

  finishStream(isError, message) {
    this.clearFlushTimer();
    this.flushDelta();
    this.task = null;

    const index = this.findMessageIndex(this.activeMessageId);
    const patch = { sending: false };

    if (index >= 0) {
      if (isError) {
        patch['messages[' + index + '].text'] = this.activeText
          ? this.activeText + '\n\n⚠️ ' + (message || '请求失败')
          : '⚠️ ' + (message || '请求失败');
        patch['messages[' + index + '].error'] = true;
        patch['messages[' + index + '].waiting'] = false;
      } else if (!this.activeText) {
        patch['messages[' + index + '].text'] = '（没有返回内容，检查模型和接口是否匹配）';
        patch['messages[' + index + '].error'] = true;
        patch['messages[' + index + '].waiting'] = false;
      } else {
        patch['messages[' + index + '].waiting'] = false;
      }
    }

    this.setData(patch, () => this.scrollToBottom());
    this.activeMessageId = '';
    this.activeText = '';
    this.deltaBuffer = '';
  },

  findMessageIndex(id) {
    const messages = this.data.messages;
    for (let index = 0; index < messages.length; index += 1) {
      if (messages[index].id === id) return index;
    }
    return -1;
  },

  copyMessage(event) {
    const index = Number(event.currentTarget.dataset.index);
    const message = this.data.messages[index];
    if (!message || !message.text) return;
    wx.setClipboardData({
      data: message.text,
      success: function () {
        wx.showToast({ title: '已复制', icon: 'none' });
      }
    });
  },

  scrollToBottom() {
    if (!this.data.messages.length) return;
    const that = this;
    this.setData({ scrollInto: '' });
    wx.nextTick(function () {
      that.setData({ scrollInto: 'bottom' });
    });
  },

  onShareAppMessage() {
    return {
      title: '卧笔 · 极简 AI 对话',
      path: '/pages/chat/chat'
    };
  }
});
