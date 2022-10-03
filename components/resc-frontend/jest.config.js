module.exports = {
  preset: '@vue/cli-plugin-unit-jest',
  testMatch: ['**/__tests__/**/*.[jt]s?(x)', '**/?(*.)+(spec|test).[jt]s?(x)'],
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['./jest.setup.js'],
  collectCoverage: true,
  coverageDirectory: 'tests/unit/reports/coverage',
  coverageReporters: ['lcov', 'text', 'cobertura'],
  collectCoverageFrom: [
    '<rootDir>/src/**/*.(js|vue)',
    '!**/node_modules/**',
    '!**/dist/**',
    '!src/main.js',
    '!src/router/**',
    '!src/configuration/**',
  ],
  coverageThreshold: {
    global: {
      branches: 95,
      functions: 95,
      lines: 95,
      statements: 95,
    },
    src: {
      branches: 60,
      functions: 60,
      lines: 80,
      statements: 80,
    },
  },
  transformIgnorePatterns: ['<rootDir>/node_modules/(?!(vue-chartjs/legacy)|(vue-sidebar-menu))'],
  transform: {
    '.*\\.(vue)$': 'vue-jest',
    '^.+\\.js$': 'babel-jest',
  },
};
