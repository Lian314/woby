/**
 * 极简 SSE 解析器：只关心 data: 行和 [DONE]。
 * 兼容 \r\n\r\n 和事件被切在多个 chunk 里的情况。
 */
class SSEParser {
  constructor(handlers) {
    this.handlers = handlers || {};
    this.buffer = '';
    this.done = false;
  }

  feed(text) {
    if (!text || this.done) return;
    this.buffer = (this.buffer + text).replace(/\r\n/g, '\n');
    if (this.buffer.charCodeAt(0) === 0xfeff) {
      this.buffer = this.buffer.slice(1);
    }

    let index = this.buffer.indexOf('\n\n');
    while (!this.done && index !== -1) {
      const raw = this.buffer.slice(0, index);
      this.buffer = this.buffer.slice(index + 2);
      this.handle(raw);
      index = this.buffer.indexOf('\n\n');
    }
  }

  flush() {
    if (this.done) return;
    const raw = this.buffer.trim();
    this.buffer = '';
    if (raw) this.handle(raw);
  }

  handle(raw) {
    const data = raw
      .split('\n')
      .filter(function (line) {
        return line.indexOf('data:') === 0;
      })
      .map(function (line) {
        return line.slice(5).replace(/^ /, '');
      })
      .join('\n')
      .trim();

    if (!data) return;

    if (data === '[DONE]') {
      this.done = true;
      if (this.handlers.onDone) this.handlers.onDone();
      return;
    }

    let payload = null;
    try {
      payload = JSON.parse(data);
    } catch (error) {
      return;
    }
    if (!payload) return;

    if (payload.error) {
      let message = '接口返回错误';
      if (typeof payload.error === 'string') {
        message = payload.error;
      } else if (payload.error.message) {
        message = payload.error.message;
      }
      this.done = true;
      if (this.handlers.onError) this.handlers.onError(message);
      return;
    }

    const choices = payload.choices || [];
    if (!choices.length) return;
    const choice = choices[0] || {};
    const delta = choice.delta || {};

    if (typeof delta.content === 'string' && delta.content) {
      if (this.handlers.onDelta) this.handlers.onDelta(delta.content);
      return;
    }

    // 少数“兼容”接口会把完整内容放在 message 里。
    if (!delta.content && choice.message && typeof choice.message.content === 'string' && choice.message.content) {
      if (this.handlers.onDelta) this.handlers.onDelta(choice.message.content);
    }
  }
}

module.exports = {
  SSEParser: SSEParser
};
