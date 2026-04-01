module.exports = {
  testEnvironment: "jsdom",
  roots: ["<rootDir>/frontend"],
  moduleFileExtensions: ["ts", "tsx", "js", "jsx", "json"],
  transform: {
    "^.+\\.(t|j)sx?$": [
      "@swc/jest",
      {
        jsc: {
          parser: {
            syntax: "typescript",
            tsx: true,
          },
          transform: {
            react: {
              runtime: "automatic",
            },
          },
        },
      },
    ],
  },
  setupFilesAfterEnv: ["<rootDir>/tests/setup/jest.setup.ts"],
  moduleNameMapper: {
    "^@/(.*)$": "<rootDir>/frontend/$1",
    "\\.(css|less|scss|sass)$": "<rootDir>/tests/mocks/styleMock.js",
    "\\.(jpg|jpeg|png|gif|webp|svg)$": "<rootDir>/tests/mocks/fileMock.js",
  },
};
