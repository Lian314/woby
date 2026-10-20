/**
 * 把用户填的 Base URL 拼成 OpenAI Chat Completions 的完整地址。
 * 默认只接受 HTTPS；打开“允许 HTTP（仅开发调试）”后才接受 HTTP。
 */
function endpoint(baseURL, allowHTTP) {
  let text = (baseURL || '').trim();
  while (text.charAt(text.length - 1) === '/') {
    text = text.slice(0, -1);
  }
  if (!text) return '';

  const isHTTPS = /^https:\/\//i.test(text);
  const isHTTP = !!allowHTTP && /^http:\/\//i.test(text);
  if (!isHTTPS && !isHTTP) return '';

  if (!/\/chat\/completions$/i.test(text)) {
    text += '/chat/completions';
  }
  return text;
}

module.exports = {
  endpoint: endpoint
};
