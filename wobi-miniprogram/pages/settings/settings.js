const storage = require('../../utils/storage');

Page({
  data: {
    baseURL: '',
    model: '',
    apiKey: '',
    systemPrompt: '',
    streaming: true,
    imageDataURL: true,
    allowHTTP: false,
    showKey: false,
    version: '1.0.0 preview'
  },

  onLoad() {
    const settings = storage.loadSettings();
    this.setData({
      baseURL: settings.baseURL,
      model: settings.model,
      apiKey: settings.apiKey,
      systemPrompt: settings.systemPrompt,
      streaming: !!settings.streaming,
      imageDataURL: settings.imageFormat !== 'raw',
      allowHTTP: !!settings.allowHTTP
    });
  },

  onInput(event) {
    const field = event.currentTarget.dataset.field;
    const patch = {};
    patch[field] = event.detail.value;
    this.setData(patch);
  },

  toggleKey() {
    this.setData({ showKey: !this.data.showKey });
  },

  onStreamingChange(event) {
    this.setData({ streaming: !!event.detail.value });
  },

  onImageDataURLChange(event) {
    this.setData({ imageDataURL: !!event.detail.value });
  },

  onAllowHTTPChange(event) {
    this.setData({ allowHTTP: !!event.detail.value });
  },

  onSystemPromptInput(event) {
    this.setData({ systemPrompt: event.detail.value });
  },

  resetPrompt() {
    this.setData({ systemPrompt: storage.SYSTEM_PROMPT });
    wx.showToast({ title: '已恢复默认提示词', icon: 'none' });
  },

  save() {
    const baseURL = (this.data.baseURL || '').trim().replace(/\/+$/, '');
    const model = (this.data.model || '').trim();
    const apiKey = (this.data.apiKey || '').trim();
    const allowHTTP = !!this.data.allowHTTP;

    const validHTTPS = /^https:\/\/[^\s/]+/i.test(baseURL);
    const validHTTP = allowHTTP && /^http:\/\/[^\s/]+/i.test(baseURL);

    if (!validHTTPS && !validHTTP) {
      wx.showToast({ title: 'Base URL 格式不对', icon: 'none' });
      return;
    }
    if (!model) {
      wx.showToast({ title: '请填写模型名', icon: 'none' });
      return;
    }
    if (!apiKey) {
      wx.showToast({ title: '请填写 API Key', icon: 'none' });
      return;
    }

    storage.saveSettings({
      baseURL: baseURL,
      model: model,
      apiKey: apiKey,
      systemPrompt: (this.data.systemPrompt || '').trim(),
      streaming: !!this.data.streaming,
      imageFormat: this.data.imageDataURL ? 'dataURL' : 'raw',
      allowHTTP: allowHTTP
    });

    wx.showToast({ title: '已保存', icon: 'success', duration: 800 });
    setTimeout(function () {
      wx.navigateBack({ delta: 1 });
    }, 500);
  }
});
