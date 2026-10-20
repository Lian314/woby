const endpoint = require('./endpoint').endpoint;
const sse = require('./sse');
const utf8 = require('./utf8');

function extractContent(data) {
  let value = data;
  if (typeof data === 'string') {
    try {
      value = JSON.parse(data);
    } catch (error) {
      return '';
    }
  }
  if (!value || !value.choices || !value.choices.length) return '';

  const choice = value.choices[0] || {};
  if (typeof choice.text === 'string' && choice.text) {
    return choice.text;
  }
  const message = choice.message;
  if (!message) return '';

  if (typeof message.content === 'string') {
    return message.content;
  }
  if (Array.isArray(message.content)) {
    return message.content
      .map(function (part) {
        return part && typeof part.text === 'string' ? part.text : '';
      })
      .join('');
  }
  return '';
}

function parseFullContent(text) {
  if (!text) return '';
  const trimmed = String(text).trim();
  if (!trimmed) return '';
  return extractContent(trimmed);
}

function errorDetail(data) {
  if (data == null || data === '') return '';
  let value = data;
  if (typeof data === 'string') {
    const trimmed = data.trim();
    if (!trimmed) return '';
    try {
      value = JSON.parse(trimmed);
    } catch (error) {
      if (trimmed.charAt(0) === '{' || trimmed.charAt(0) === '[') return '';
      return trimmed.slice(0, 300);
    }
  }
  if (!value || typeof value !== 'object') return '';

  if (value.error) {
    if (typeof value.error === 'string') return value.error;
    if (value.error.message) return String(value.error.message);
  }
  if (value.message) return String(value.message);
  if (value.msg) return String(value.msg);
  return '';
}

function errorMessage(data, statusCode) {
  const detail = errorDetail(data);
  if (detail) return detail;
  if (statusCode) return '请求失败（HTTP ' + statusCode + '）';
  return '请求失败';
}

function buildContent(message, imageFormat) {
  const text = message.text || '';
  const images = message.images || [];
  if (!images.length) return text;

  const parts = [
    {
      type: 'text',
      text: text || '看看这张图片。'
    }
  ];

  images.forEach(function (image) {
    if (!image || !image.base64) return;
    const mime = image.mime || 'image/jpeg';
    const url = imageFormat === 'raw'
      ? image.base64
      : 'data:' + mime + ';base64,' + image.base64;
    parts.push({
      type: 'image_url',
      image_url: { url: url }
    });
  });

  return parts;
}

function buildMessages(history, systemPrompt, imageFormat) {
  const messages = [];
  const system = (systemPrompt || '').trim();
  if (system) {
    messages.push({ role: 'system', content: system });
  }

  (history || []).forEach(function (message) {
    if (!message) return;
    if (message.role === 'user') {
      messages.push({
        role: 'user',
        content: buildContent(message, imageFormat)
      });
    } else if (message.role === 'assistant' && message.text && !message.error) {
      messages.push({ role: 'assistant', content: message.text });
    }
  });

  return messages;
}

function makeBody(settings, messages, stream) {
  return {
    model: (settings.model || '').trim(),
    messages: messages,
    stream: !!stream
  };
}

function requestHeader(settings, stream) {
  return {
    'Content-Type': 'application/json',
    Authorization: 'Bearer ' + ((settings.apiKey || '').trim()),
    Accept: stream ? 'text/event-stream' : 'application/json'
  };
}

function plainChat(options) {
  const settings = options.settings;
  const url = endpoint(settings.baseURL, settings.allowHTTP);
  if (!url) {
    options.onError('Base URL 无效，请到设置里检查（必须是 https://；如果开启“允许 HTTP”，也可以用 http://）。');
    return { abort: function () {} };
  }

  const messages = buildMessages(options.history, settings.systemPrompt, settings.imageFormat);
  const body = JSON.stringify(makeBody(settings, messages, false));

  let task = null;
  let settled = false;
  let aborted = false;

  try {
    task = wx.request({
      url: url,
      method: 'POST',
      timeout: 60000,
      header: requestHeader(settings, false),
      data: body,
      dataType: 'json',
      success(res) {
        if (settled || aborted) return;
        settled = true;
        const status = res.statusCode || 0;
        if (status < 200 || status >= 300) {
          options.onError(errorMessage(res.data, status));
          return;
        }
        const content = extractContent(res.data);
        if (!content) {
          options.onError(errorDetail(res.data) || '没有返回内容，检查模型是否支持该接口。');
          return;
        }
        options.onDelta(content);
        options.onDone();
      },
      fail(err) {
        if (settled || aborted) return;
        settled = true;
        options.onError((err && err.errMsg) ? err.errMsg : '网络请求失败');
      }
    });
  } catch (error) {
    options.onError((error && error.message) ? error.message : '请求发起失败');
    return { abort: function () {} };
  }

  return {
    abort: function () {
      if (settled) return;
      aborted = true;
      settled = true;
      if (task && typeof task.abort === 'function') task.abort();
    }
  };
}

function streamChat(options) {
  const settings = options.settings;
  if (!settings.streaming) {
    return plainChat(options);
  }

  const url = endpoint(settings.baseURL, settings.allowHTTP);
  if (!url) {
    options.onError('Base URL 无效，请到设置里检查（必须是 https://；如果开启“允许 HTTP”，也可以用 http://）。');
    return { abort: function () {} };
  }

  const messages = buildMessages(options.history, settings.systemPrompt, settings.imageFormat);
  const body = JSON.stringify(makeBody(settings, messages, true));

  let task = null;
  let settled = false;
  let aborted = false;
  let sawChunk = false;
  let gotDelta = false;
  let raw = '';

  const finishDone = function () {
    if (settled) return;
    settled = true;
    options.onDone();
  };

  const finishError = function (message) {
    if (settled) return;
    settled = true;
    options.onError(message || '请求失败');
  };

  const parser = new sse.SSEParser({
    onDelta(text) {
      gotDelta = true;
      options.onDelta(text);
    },
    onDone() {
      finishDone();
    },
    onError(message) {
      finishError(message);
    }
  });

  const decoder = new utf8.Utf8StreamDecoder();

  const feed = function (data) {
    const text = decoder.decode(data);
    if (!text) return;
    raw += text;
    parser.feed(text);
  };

  try {
    task = wx.request({
      url: url,
      method: 'POST',
      timeout: 60000,
      header: requestHeader(settings, true),
      data: body,
      enableChunked: true,
      responseType: 'arraybuffer',
      success(res) {
        if (settled || aborted) return;

        const status = res.statusCode || 0;
        const bodyText = (!sawChunk && res.data) ? decoder.decode(res.data) : '';
        if (bodyText) raw += bodyText;

        if (status < 200 || status >= 300) {
          finishError(errorMessage(raw, status));
          return;
        }

        if (bodyText) {
          parser.feed(bodyText);
        }
        parser.flush();
        if (settled || aborted) return;

        if (!gotDelta) {
          const content = parseFullContent(raw);
          if (content) {
            gotDelta = true;
            options.onDelta(content);
          } else {
            const trimmed = raw.trim();
            const detail = trimmed.charAt(0) === '{' ? errorDetail(trimmed) : '';
            finishError(detail || '没有返回内容，检查模型是否支持该接口。');
            return;
          }
        }

        finishDone();
      },
      fail(err) {
        if (settled || aborted) return;
        finishError((err && err.errMsg) ? err.errMsg : '网络请求失败');
      }
    });
  } catch (error) {
    finishError((error && error.message) ? error.message : '请求发起失败');
    return { abort: function () {} };
  }

  if (task && typeof task.onChunkReceived === 'function') {
    task.onChunkReceived(function (res) {
      if (settled || aborted) return;
      sawChunk = true;
      feed(res.data);
    });
  }

  return {
    abort: function () {
      if (settled) return;
      aborted = true;
      settled = true;
      if (task && typeof task.abort === 'function') task.abort();
    }
  };
}

module.exports = {
  streamChat: streamChat
};
