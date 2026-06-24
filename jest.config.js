module.exports = {
  testEnvironment: "jsdom",
  roots: ["<rootDir>/tests/js"],
  setupFiles: ["<rootDir>/tests/js/setup.js"],
  moduleDirectories: ["node_modules", "<rootDir>"],
  testMatch: ["**/tests/js/**/*.test.js"],
  collectCoverageFrom: ["zensical_macros_utils/static/js/x-twitter-widget.js"],
  coverageDirectory: "coverage",
  coverageThreshold: {
    global: {
      branches: 100,
      functions: 100,
      lines: 100,
      statements: 100,
    },
  },
  transform: {
    "^.+\\.js$": "babel-jest",
  },
};
