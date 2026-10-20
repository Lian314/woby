const SETTINGS_KEY = 'wobi_settings_v1';

const SYSTEM_PROMPT =
  '你是「卧笔」，一个简洁、可靠的中文 AI 助手。回答尽量直接，少客套。遇到图片时，先说出画面里的关键信息，再回答用户的问题。';

function defaultSettings() {
  return {
    baseURL: '',
    model: '',
    apiKey: '',
    systemPrompt: SYSTEM_PROMPT,
    streaming: true,
    imageFormat: 'dataURL',
    allowHTTP: false
  };
}

function loadSettings() {
  let stored = null;
  try {
    stored = wx.getStorageSync(SETTINGS_KEY);
  } catch (error) {
    stored = null;
  }
  if (!stored || typeof stored !== 'object' || Array.isArray(stored)) {
    stored = {};
  }
  return Object.assign(defaultSettings(), stored);
}

function saveSettings(settings) {
  wx.setStorageSync(SETTINGS_KEY, settings);
}

module.exports = {
  SETTINGS_KEY: SETTINGS_KEY,
  SYSTEM_PROMPT: SYSTEM_PROMPT,
  defaultSettings: defaultSettings,
  loadSettings: loadSettings,
  saveSettings: saveSettings
};
