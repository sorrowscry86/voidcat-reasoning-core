# MCP Server Chart - Installation and Demonstration

## ✅ Installation Complete

The MCP server from `https://github.com/antvis/mcp-server-chart` has been successfully installed with the server name `github.com/antvis/mcp-server-chart` in the blackbox_mcp_settings.json file.

## 📋 Configuration Details

The server has been configured with:
- **Server Name**: `github.com/antvis/mcp-server-chart`
- **Command**: `cmd /c npx -y @antv/mcp-server-chart`
- **Transport**: stdio (default)
- **Status**: Ready for use

## 🎯 Available Chart Types

The server provides 25+ chart generation tools:

### Basic Charts
- `generate_line_chart` - Line charts for trends over time
- `generate_bar_chart` - Horizontal bar charts for category comparison
- `generate_column_chart` - Vertical column charts for category comparison
- `generate_pie_chart` - Pie charts for proportion display
- `generate_area_chart` - Area charts for cumulative trends

### Statistical Charts
- `generate_histogram_chart` - Histograms for data distribution
- `generate_boxplot_chart` - Box plots for statistical summaries
- `generate_violin_chart` - Violin plots for detailed distributions
- `generate_scatter_chart` - Scatter plots for variable relationships

### Advanced Charts
- `generate_radar_chart` - Radar charts for multi-dimensional data
- `generate_sankey_chart` - Sankey diagrams for flow visualization
- `generate_treemap_chart` - Treemaps for hierarchical data
- `generate_network_graph` - Network graphs for relationships
- `generate_funnel_chart` - Funnel charts for process stages

### Specialized Charts
- `generate_word_cloud_chart` - Word clouds for text frequency
- `generate_heatmap_chart` - Heatmaps for matrix data
- `generate_gauge_chart` - Gauges for KPI metrics
- `generate_liquid_chart` - Liquid charts for percentage display

### Geographic Charts
- `generate_district_map` - Administrative division maps
- `generate_pin_map` - Point of interest maps
- `generate_path_map` - Route planning maps

### Business Charts
- `generate_organization_chart` - Organizational structures
- `generate_mind_map` - Mind maps for brainstorming
- `generate_flow_diagram` - Process flow diagrams
- `generate_fishbone_diagram` - Root cause analysis (Ishikawa)

## 🚀 Usage Examples

### Example 1: Line Chart
```json
{
  "tool": "generate_line_chart",
  "parameters": {
    "data": [
      {"month": "Jan", "sales": 100},
      {"month": "Feb", "sales": 150},
      {"month": "Mar", "sales": 200}
    ],
    "title": "Monthly Sales Trend",
    "xField": "month",
    "yField": "sales"
  }
}
```

### Example 2: Bar Chart
```json
{
  "tool": "generate_bar_chart",
  "parameters": {
    "data": [
      {"category": "Product A", "value": 45},
      {"category": "Product B", "value": 78},
      {"category": "Product C", "value": 32}
    ],
    "title": "Product Performance",
    "xField": "value",
    "yField": "category"
  }
}
```

### Example 3: Pie Chart
```json
{
  "tool": "generate_pie_chart",
  "parameters": {
    "data": [
      {"type": "Desktop", "value": 45},
      {"type": "Mobile", "value": 30},
      {"type": "Tablet", "value": 25}
    ],
    "title": "Device Usage Distribution"
  }
}
```

## 🔧 Environment Variables (Optional)

The server supports these optional environment variables:
- `VIS_REQUEST_SERVER`: Custom chart generation service URL
- `SERVICE_ID`: Service identifier for chart generation records
- `DISABLED_TOOLS`: Comma-separated list of tools to disable

## 📊 Demonstration

The server is now ready to generate charts. You can use any of the 25+ available chart types by calling the appropriate tool with your data.

**Note**: The server will automatically restart to pick up the new configuration. If you encounter connection issues, please restart your VS Code instance.
