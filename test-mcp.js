#!/usr/bin/env node

console.log('Testing MCP Server Configuration...\n');

const config = require('./mcp.json');

console.log('MCP Servers configured:');
Object.entries(config.mcpServers).forEach(([name, server]) => {
    console.log(`\n${name}:`);
    console.log(`  Command: ${server.command}`);
    console.log(`  Args: ${server.args.join(' ')}`);
    if (server.env) {
        console.log('  Environment:');
        Object.entries(server.env).forEach(([key, value]) => {
            console.log(`    ${key}: ${value}`);
        });
    }
});

console.log('\nConfiguration file is valid!');