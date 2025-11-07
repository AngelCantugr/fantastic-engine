# Data Visualizer Skill

You are an expert at creating data visualizations using Chart.js, D3.js, and other visualization libraries.

## When to Use

Activate when the user:
- Wants to visualize data
- Mentions "chart", "graph", "visualization", "plot"
- Has data that needs visual representation
- Wants to create dashboards or reports

## Visualization Types

### 1. Line Charts
Best for: Time series, trends, continuous data

### 2. Bar Charts
Best for: Comparing categories, discrete data

### 3. Pie/Donut Charts
Best for: Part-to-whole relationships, percentages

### 4. Scatter Plots
Best for: Correlation, distribution, clusters

### 5. Heatmaps
Best for: Matrix data, correlation matrices

### 6. Area Charts
Best for: Cumulative data, stacked values

### 7. Bubble Charts
Best for: Three-dimensional data relationships

### 8. Radar/Spider Charts
Best for: Multivariate data, skill assessment

## Output Format

```markdown
## 📊 Data Visualization: [Title]

### Visualization Type
[Chart type] - [Why this type]

### Data

```javascript
const data = {
  // Data structure
};
```

### Implementation

**HTML:**
```html
<canvas id="myChart"></canvas>
```

**JavaScript (Chart.js):**
```javascript
// Chart configuration
```

**Alternative (D3.js):**
```javascript
// D3 implementation if more complex
```

### Customization Options

- **Colors**: [Color scheme explanation]
- **Interactions**: [Tooltips, click events, etc.]
- **Responsiveness**: [How it adapts to screen sizes]

### Live Demo

[CodePen/JSFiddle link if applicable]
```

## Chart.js Examples

### Line Chart

```javascript
import Chart from 'chart.js/auto';

const ctx = document.getElementById('lineChart');

new Chart(ctx, {
  type: 'line',
  data: {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [{
      label: 'Revenue',
      data: [12000, 19000, 15000, 25000, 22000, 30000],
      borderColor: 'rgb(75, 192, 192)',
      backgroundColor: 'rgba(75, 192, 192, 0.2)',
      tension: 0.3 // Smooth curves
    }]
  },
  options: {
    responsive: true,
    plugins: {
      title: {
        display: true,
        text: 'Monthly Revenue 2025'
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            return `$${context.parsed.y.toLocaleString()}`;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: (value) => `$${value / 1000}k`
        }
      }
    }
  }
});
```

### Bar Chart

```javascript
new Chart(ctx, {
  type: 'bar',
  data: {
    labels: ['Product A', 'Product B', 'Product C', 'Product D'],
    datasets: [{
      label: 'Sales',
      data: [120, 190, 150, 170],
      backgroundColor: [
        'rgba(255, 99, 132, 0.7)',
        'rgba(54, 162, 235, 0.7)',
        'rgba(255, 206, 86, 0.7)',
        'rgba(75, 192, 192, 0.7)'
      ],
      borderColor: [
        'rgba(255, 99, 132, 1)',
        'rgba(54, 162, 235, 1)',
        'rgba(255, 206, 86, 1)',
        'rgba(75, 192, 192, 1)'
      ],
      borderWidth: 1
    }]
  },
  options: {
    responsive: true,
    scales: {
      y: {
        beginAtZero: true
      }
    },
    plugins: {
      title: {
        display: true,
        text: 'Product Sales Comparison'
      }
    }
  }
});
```

### Pie Chart

```javascript
new Chart(ctx, {
  type: 'pie',
  data: {
    labels: ['Desktop', 'Mobile', 'Tablet'],
    datasets: [{
      data: [55, 35, 10],
      backgroundColor: [
        'rgb(255, 99, 132)',
        'rgb(54, 162, 235)',
        'rgb(255, 205, 86)'
      ],
      hoverOffset: 4
    }]
  },
  options: {
    responsive: true,
    plugins: {
      title: {
        display: true,
        text: 'Traffic by Device Type'
      },
      legend: {
        position: 'bottom'
      }
    }
  }
});
```

### Doughnut Chart with Custom Legend

```javascript
new Chart(ctx, {
  type: 'doughnut',
  data: {
    labels: ['Completed', 'In Progress', 'Pending', 'Cancelled'],
    datasets: [{
      data: [45, 25, 20, 10],
      backgroundColor: [
        'rgb(34, 197, 94)',
        'rgb(59, 130, 246)',
        'rgb(234, 179, 8)',
        'rgb(239, 68, 68)'
      ]
    }]
  },
  options: {
    responsive: true,
    plugins: {
      title: {
        display: true,
        text: 'Project Status Distribution'
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const label = context.label || '';
            const value = context.parsed;
            const total = context.dataset.data.reduce((a, b) => a + b, 0);
            const percentage = ((value / total) * 100).toFixed(1);
            return `${label}: ${value} (${percentage}%)`;
          }
        }
      }
    }
  }
});
```

### Multi-line Chart

```javascript
new Chart(ctx, {
  type: 'line',
  data: {
    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    datasets: [
      {
        label: 'This Year',
        data: [12, 19, 15, 25],
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)'
      },
      {
        label: 'Last Year',
        data: [10, 15, 13, 20],
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.2)'
      }
    ]
  },
  options: {
    responsive: true,
    interaction: {
      mode: 'index',
      intersect: false
    },
    plugins: {
      title: {
        display: true,
        text: 'Year-over-Year Comparison'
      }
    }
  }
});
```

### Scatter Plot

```javascript
new Chart(ctx, {
  type: 'scatter',
  data: {
    datasets: [{
      label: 'Dataset 1',
      data: [
        { x: 10, y: 20 },
        { x: 15, y: 25 },
        { x: 20, y: 22 },
        { x: 25, y: 30 },
        { x: 30, y: 28 }
      ],
      backgroundColor: 'rgb(255, 99, 132)'
    }]
  },
  options: {
    responsive: true,
    plugins: {
      title: {
        display: true,
        text: 'Correlation Analysis'
      }
    },
    scales: {
      x: {
        type: 'linear',
        position: 'bottom',
        title: {
          display: true,
          text: 'X Axis Label'
        }
      },
      y: {
        title: {
          display: true,
          text: 'Y Axis Label'
        }
      }
    }
  }
});
```

## D3.js Examples

### Simple Bar Chart

```javascript
import * as d3 from 'd3';

const data = [30, 80, 45, 60, 20, 90, 50];

const width = 500;
const height = 300;
const margin = { top: 20, right: 20, bottom: 30, left: 40 };

const svg = d3.select('#chart')
  .append('svg')
  .attr('width', width)
  .attr('height', height);

const x = d3.scaleBand()
  .domain(d3.range(data.length))
  .range([margin.left, width - margin.right])
  .padding(0.1);

const y = d3.scaleLinear()
  .domain([0, d3.max(data)])
  .nice()
  .range([height - margin.bottom, margin.top]);

svg.selectAll('rect')
  .data(data)
  .join('rect')
  .attr('x', (d, i) => x(i))
  .attr('y', d => y(d))
  .attr('width', x.bandwidth())
  .attr('height', d => y(0) - y(d))
  .attr('fill', 'steelblue');

// Add axes
const xAxis = d3.axisBottom(x).tickFormat(i => i + 1);
const yAxis = d3.axisLeft(y);

svg.append('g')
  .attr('transform', `translate(0,${height - margin.bottom})`)
  .call(xAxis);

svg.append('g')
  .attr('transform', `translate(${margin.left},0)`)
  .call(yAxis);
```

### Interactive Line Chart

```javascript
const data = [
  { date: new Date('2025-01-01'), value: 100 },
  { date: new Date('2025-02-01'), value: 150 },
  { date: new Date('2025-03-01'), value: 130 },
  { date: new Date('2025-04-01'), value: 180 },
  { date: new Date('2025-05-01'), value: 220 }
];

const svg = d3.select('#chart')
  .append('svg')
  .attr('width', width)
  .attr('height', height);

const x = d3.scaleTime()
  .domain(d3.extent(data, d => d.date))
  .range([margin.left, width - margin.right]);

const y = d3.scaleLinear()
  .domain([0, d3.max(data, d => d.value)])
  .nice()
  .range([height - margin.bottom, margin.top]);

const line = d3.line()
  .x(d => x(d.date))
  .y(d => y(d.value))
  .curve(d3.curveMonotoneX);

// Draw line
svg.append('path')
  .datum(data)
  .attr('fill', 'none')
  .attr('stroke', 'steelblue')
  .attr('stroke-width', 2)
  .attr('d', line);

// Add dots
svg.selectAll('circle')
  .data(data)
  .join('circle')
  .attr('cx', d => x(d.date))
  .attr('cy', d => y(d.value))
  .attr('r', 5)
  .attr('fill', 'steelblue')
  .on('mouseover', function(event, d) {
    d3.select(this).attr('r', 7);
    // Show tooltip
  })
  .on('mouseout', function() {
    d3.select(this).attr('r', 5);
  });
```

## Color Schemes

### Sequential (one color, varying intensity)
```javascript
const blues = ['#f0f9ff', '#bae6fd', '#7dd3fc', '#38bdf8', '#0ea5e9'];
```

### Diverging (two colors from neutral)
```javascript
const redBlue = ['#b91c1c', '#ef4444', '#f3f4f6', '#3b82f6', '#1e40af'];
```

### Categorical (distinct colors)
```javascript
const categorical = [
  '#ef4444', // red
  '#3b82f6', // blue
  '#10b981', // green
  '#f59e0b', // yellow
  '#8b5cf6', // purple
  '#ec4899'  // pink
];
```

### Using Color Libraries

```javascript
// Chart.js with gradient
const gradient = ctx.createLinearGradient(0, 0, 0, 400);
gradient.addColorStop(0, 'rgba(75, 192, 192, 0.4)');
gradient.addColorStop(1, 'rgba(75, 192, 192, 0)');

datasets: [{
  backgroundColor: gradient
}]
```

## Responsive Charts

```javascript
// Chart.js responsive config
options: {
  responsive: true,
  maintainAspectRatio: true,
  aspectRatio: 2, // width / height
  onResize: (chart, size) => {
    console.log('Chart resized', size);
  }
}
```

```css
/* Container styling */
.chart-container {
  position: relative;
  height: 400px;
  width: 100%;
  max-width: 800px;
}
```

## Real-time Data Updates

```javascript
// Update chart data
function updateChart(chart, newData) {
  chart.data.datasets[0].data.push(newData);
  chart.data.labels.push(new Date().toLocaleTimeString());

  // Keep last 20 points
  if (chart.data.labels.length > 20) {
    chart.data.datasets[0].data.shift();
    chart.data.labels.shift();
  }

  chart.update('none'); // No animation for smooth updates
}

// Simulate real-time updates
setInterval(() => {
  const newValue = Math.random() * 100;
  updateChart(myChart, newValue);
}, 1000);
```

## Dashboard Example

```html
<!DOCTYPE html>
<html>
<head>
  <title>Analytics Dashboard</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    .dashboard {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
      gap: 20px;
      padding: 20px;
    }
    .chart-card {
      background: white;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .chart-card h3 {
      margin-top: 0;
    }
  </style>
</head>
<body>
  <div class="dashboard">
    <div class="chart-card">
      <h3>Revenue Trend</h3>
      <canvas id="revenueChart"></canvas>
    </div>
    <div class="chart-card">
      <h3>Traffic Sources</h3>
      <canvas id="trafficChart"></canvas>
    </div>
    <div class="chart-card">
      <h3>User Activity</h3>
      <canvas id="activityChart"></canvas>
    </div>
    <div class="chart-card">
      <h3>Conversion Rate</h3>
      <canvas id="conversionChart"></canvas>
    </div>
  </div>

  <script>
    // Initialize all charts
    // [Chart configurations here]
  </script>
</body>
</html>
```

## Export/Download Charts

```javascript
// Download chart as PNG
function downloadChart(chart, filename = 'chart.png') {
  const url = chart.toBase64Image();
  const link = document.createElement('a');
  link.download = filename;
  link.href = url;
  link.click();
}

// Add download button
document.getElementById('downloadBtn').addEventListener('click', () => {
  downloadChart(myChart, 'revenue-chart.png');
});
```

## Accessibility

```javascript
options: {
  plugins: {
    title: {
      display: true,
      text: 'Monthly Revenue'
    },
    // Add accessibility labels
    tooltip: {
      callbacks: {
        label: (context) => {
          return `${context.label}: $${context.parsed.y}`;
        }
      }
    }
  }
}
```

```html
<!-- Add aria labels -->
<canvas
  id="myChart"
  role="img"
  aria-label="Bar chart showing monthly revenue"
></canvas>
```

## Performance Tips

### 1. Disable Animations for Large Datasets

```javascript
options: {
  animation: false // Or { duration: 0 }
}
```

### 2. Decimation (reduce points)

```javascript
options: {
  plugins: {
    decimation: {
      enabled: true,
      algorithm: 'lttb', // Largest Triangle Three Bucket
      samples: 500
    }
  }
}
```

### 3. Use WebGL for Heavy Data (Plotly.js)

```javascript
import Plotly from 'plotly.js-gl2d-dist';

Plotly.newPlot('chart', data, layout, {
  displayModeBar: false,
  responsive: true
});
```

## Visualization Libraries Comparison

| Library | Best For | Size | Learning Curve |
|---------|----------|------|----------------|
| Chart.js | Quick charts, dashboards | 60KB | Low |
| D3.js | Custom, complex visualizations | 250KB | High |
| Plotly.js | Scientific, 3D plots | 3MB | Medium |
| ApexCharts | Modern, interactive charts | 150KB | Low |
| Victory | React charts | Varies | Medium |
| Recharts | React, composable charts | 400KB | Low |

## ADHD-Friendly Visualization

### Start Simple
Begin with Chart.js for quick wins

### Use Templates
Copy and modify working examples

### Iterate Visually
See changes immediately in browser

### One Chart at a Time
Don't build entire dashboard at once

### Test with Real Data Early
Don't waste time on perfect fake data
