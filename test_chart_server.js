// Test script to demonstrate MCP server chart capabilities
const { spawn } = require('child_process');
const { writeFileSync } = require('fs');

// Test data for line chart
const testData = {
  type: 'line',
  data: [
    { time: '2024-01', value: 100 },
    { time: '2024-02', value: 150 },
    { time: '2024-03', value: 200 },
    { time: '2024-04', value: 180 },
    { time: '2024-05', value: 250 },
    { time: '2024-06', value: 300 }
  ],
  title: 'Monthly Sales Data',
  xField: 'time',
  yField: 'value'
};

console.log('Testing MCP Server Chart capabilities...');
console.log('Test data:', JSON.stringify(testData, null, 2));

// This would normally be called via MCP protocol
// For demonstration, we'll show the expected input format
console.log('\nExpected MCP tool call:');
console.log('Tool: generate_line_chart');
console.log('Parameters:', testData);
console.log('\nThis would generate a line chart showing sales trends over time.');
