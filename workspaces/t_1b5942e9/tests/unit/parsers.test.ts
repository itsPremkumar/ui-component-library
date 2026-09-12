import { describe, it, expect } from 'vitest';
import { parseJUnitXML, parseJSONReport, parseTestReport, compareReports } from '../../src/lib/parsers';
import { generateSampleReport } from '../../src/lib/sampleData';

describe('parseJUnitXML', () => {
  it('parses a simple JUnit XML report', () => {
    const xml = `<?xml version="1.0" encoding="UTF-8"?>
<testsuites name="Test Suite" tests="2" failures="1">
  <testsuite name="Math Tests" tests="2" failures="1">
    <testcase name="should add numbers" classname="Math Tests" time="0.001" />
    <testcase name="should subtract numbers" classname="Math Tests" time="0.002">
      <failure message="Expected 2" type="AssertionError">Expected 2 but got 3</failure>
    </testcase>
  </testsuite>
</testsuites>`;

    const report = parseJUnitXML(xml);
    expect(report.summary.total).toBe(2);
    expect(report.summary.passed).toBe(1);
    expect(report.summary.failed).toBe(1);
    expect(report.suites.length).toBe(1);
    expect(report.suites[0].tests[1].error?.message).toBe('Expected 2');
  });

  it('handles skipped tests', () => {
    const xml = `<?xml version="1.0" encoding="UTF-8"?>
<testsuites name="Test Suite" tests="1" skipped="1">
  <testsuite name="Skipped Suite" tests="1" skipped="1">
    <testcase name="should skip this" classname="Skipped Suite" time="0">
      <skipped />
    </testcase>
  </testsuite>
</testsuites>`;

    const report = parseJUnitXML(xml);
    expect(report.summary.skipped).toBe(1);
    expect(report.suites[0].tests[0].status).toBe('skipped');
  });

  it('throws on invalid XML', () => {
    expect(() => parseJUnitXML('not xml at all')).toThrow();
  });
});

describe('parseJSONReport', () => {
  it('parses Jest format', () => {
    const jestData = JSON.stringify({
      startTime: Date.now(),
      testResults: [
        {
          name: 'test.spec.ts',
          results: [
            { title: 'passes', status: 'passed', duration: 10, failureMessages: [] },
            { title: 'fails', status: 'failed', duration: 20, failureMessages: ['Error: expected true'] },
          ],
        },
      ],
    });

    const report = parseJSONReport(jestData);
    expect(report.summary.total).toBe(2);
    expect(report.summary.passed).toBe(1);
    expect(report.summary.failed).toBe(1);
  });

  it('parses simple array format', () => {
    const data = JSON.stringify([
      { name: 'test1', suite: 'Suite A', status: 'passed', duration: 100 },
      { name: 'test2', suite: 'Suite A', status: 'failed', duration: 200 },
      { name: 'test3', suite: 'Suite B', status: 'skipped', duration: 0 },
    ]);

    const report = parseJSONReport(data);
    expect(report.summary.total).toBe(3);
    expect(report.summary.passed).toBe(1);
    expect(report.summary.failed).toBe(1);
    expect(report.summary.skipped).toBe(1);
  });
});

describe('parseTestReport', () => {
  it('auto-detects XML format', () => {
    const xml = `<?xml version="1.0" encoding="UTF-8"?>
<testsuites name="Test Suite" tests="1">
  <testsuite name="Suite" tests="1">
    <testcase name="test" classname="Suite" time="0.001" />
  </testsuite>
</testsuites>`;

    const report = parseTestReport(xml);
    expect(report.summary.total).toBe(1);
  });

  it('auto-detects JSON format', () => {
    const json = JSON.stringify([{ name: 'test', suite: 'Suite', status: 'passed', duration: 100 }]);
    const report = parseTestReport(json);
    expect(report.summary.total).toBe(1);
  });

  it('throws on unknown format', () => {
    expect(() => parseTestReport('random text')).toThrow();
  });
});

describe('compareReports', () => {
  it('identifies added tests', () => {
    const reportA = generateSampleReport();
    const reportB = generateSampleReport();

    // Add a unique test to report B
    reportB.suites[0].tests.push({
      id: 'unique-test',
      name: 'unique test',
      suite: reportB.suites[0].name,
      status: 'passed',
      duration: 100,
      startTime: new Date().toISOString(),
      endTime: new Date().toISOString(),
    });

    const result = compareReports(reportA, reportB);
    expect(result.added.length).toBeGreaterThan(0);
    expect(result.added.some((t) => t.name === 'unique test')).toBe(true);
  });

  it('identifies status changes', () => {
    const reportA = generateSampleReport();
    const reportB = generateSampleReport();

    // Force a status change
    if (reportA.suites[0].tests[0] && reportB.suites[0].tests[0]) {
      reportA.suites[0].tests[0].status = 'passed';
      reportB.suites[0].tests[0].status = 'failed';
    }

    const result = compareReports(reportA, reportB);
    expect(result.statusChanged.length).toBeGreaterThan(0);
  });
});

describe('generateSampleReport', () => {
  it('generates a valid report', () => {
    const report = generateSampleReport();
    expect(report.id).toBeDefined();
    expect(report.summary.total).toBeGreaterThan(0);
    expect(report.suites.length).toBeGreaterThan(0);
    expect(report.summary.passRate).toBeGreaterThanOrEqual(0);
    expect(report.summary.passRate).toBeLessThanOrEqual(100);
  });

  it('has all required fields', () => {
    const report = generateSampleReport();
    const test = report.suites[0].tests[0];
    expect(test.id).toBeDefined();
    expect(test.name).toBeDefined();
    expect(test.suite).toBeDefined();
    expect(test.status).toBeDefined();
    expect(test.duration).toBeGreaterThanOrEqual(0);
  });
});
