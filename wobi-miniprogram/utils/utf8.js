/**
 * 微信小程序的请求分块是 ArrayBuffer；小程序环境不一定有 TextDecoder，
 * 这里实现一个有状态的 UTF-8 解码器，能处理汉字被切在两个 chunk 里的情况。
 */
function codesToString(codes) {
  let out = '';
  for (let index = 0; index < codes.length; index += 4096) {
    out += String.fromCharCode.apply(null, codes.slice(index, index + 4096));
  }
  return out;
}

class Utf8StreamDecoder {
  constructor() {
    this.pending = [];
  }

  decode(input) {
    if (input == null) return '';
    if (typeof input === 'string') return input;

    let bytes = null;
    if (input instanceof ArrayBuffer) {
      bytes = new Uint8Array(input);
    } else if (ArrayBuffer.isView(input)) {
      bytes = new Uint8Array(input.buffer, input.byteOffset, input.byteLength);
    } else if (Array.isArray(input)) {
      bytes = new Uint8Array(input);
    }
    if (!bytes || !bytes.length) return '';

    const source = this.pending.length
      ? this.pending.concat(Array.from(bytes))
      : Array.from(bytes);

    const codes = [];
    let index = 0;

    while (index < source.length) {
      const first = source[index];

      if (first < 0x80) {
        codes.push(first);
        index += 1;
        continue;
      }

      let need = 0;
      let codePoint = 0;

      if ((first & 0xe0) === 0xc0) {
        need = 1;
        codePoint = first & 0x1f;
      } else if ((first & 0xf0) === 0xe0) {
        need = 2;
        codePoint = first & 0x0f;
      } else if ((first & 0xf8) === 0xf0) {
        need = 3;
        codePoint = first & 0x07;
      } else {
        index += 1;
        continue;
      }

      if (index + need >= source.length) {
        break;
      }

      let valid = true;
      for (let offset = 1; offset <= need; offset += 1) {
        const next = source[index + offset];
        if ((next & 0xc0) !== 0x80) {
          valid = false;
          break;
        }
        codePoint = (codePoint << 6) | (next & 0x3f);
      }

      if (!valid) {
        index += 1;
        continue;
      }

      if (codePoint > 0x10ffff || (codePoint >= 0xd800 && codePoint <= 0xdfff)) {
        index += need + 1;
        continue;
      }

      if (codePoint > 0xffff) {
        codePoint -= 0x10000;
        codes.push(0xd800 + (codePoint >> 10), 0xdc00 + (codePoint & 0x3ff));
      } else {
        codes.push(codePoint);
      }

      index += need + 1;
    }

    this.pending = source.slice(index);
    return codesToString(codes);
  }
}

module.exports = {
  Utf8StreamDecoder: Utf8StreamDecoder
};
