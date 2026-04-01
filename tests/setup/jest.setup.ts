import "@testing-library/jest-dom";
import { TextDecoder, TextEncoder } from "node:util";

if (!global.TextEncoder) {
  // react-router depends on TextEncoder in Jest's jsdom runtime.
  global.TextEncoder = TextEncoder as typeof global.TextEncoder;
}

if (!global.TextDecoder) {
  global.TextDecoder = TextDecoder as typeof global.TextDecoder;
}
