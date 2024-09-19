import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

# Sample DataFrame with more rows
df = pd.DataFrame({
    "Name": ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Hannah", "Ivy", "Jack"],
    "Age": [24, 27, 22, 30, 28, 25, 29, 32, 21, 26],
    "City": ["New York", "San Francisco", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas"]
})

df = df_in_progress.iloc [:, :-2]

# Generate a Plotly table
table = go.Figure(data=[go.Table(
    header=dict(values=df.columns.tolist(), fill_color='paleturquoise', align='left'),
    cells=dict(values=[df[col].tolist() for col in df.columns],
               fill_color='lavender', align='left'))
])

# # Add a simple plot
# fig = go.Figure(data=go.Bar(x=df["Name"], y=df["Age"], marker_color='indianred'))
# fig.update_layout(title_text='Age of Individuals')

# Save both the Plotly table and plot to HTML
table_html = pio.to_html(table, full_html=False)
plot_html = pio.to_html(fig, full_html=False)

# Combine the HTML content with DataTables pagination set to 50 rows per page
html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Interactive Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/jquery@3.6.0/dist/jquery.min.js"></script>
    <script src="https://cdn.datatables.net/1.10.25/js/jquery.dataTables.min.js"></script>
    <link rel="stylesheet" href="https://cdn.datatables.net/1.10.25/css/jquery.dataTables.min.css">
</head>
<body>
    <h1>Sample Dashboard</h1>

    <!-- First instance of the table -->
    <h2>Interactive Table</h2>
    <table id="table1" class="display">
        <thead>
            <tr>
                {''.join([f'<th>{col}</th>' for col in df.columns])}
            </tr>
        </thead>
        <tbody>
            {''.join([f'<tr>{"".join([f"<td>{row[col]}</td>" for col in df.columns])}</tr>' for _, row in df.iterrows()])}
        </tbody>
    </table>

    <!-- Bar plot -->
    <h2>Bar Plot</h2>
    {plot_html}

    <!-- Second instance of the table -->
    <h2>Interactive Table</h2>
    <table id="table2" class="display">
        <thead>
            <tr>
                {''.join([f'<th>{col}</th>' for col in df.columns])}
            </tr>
        </thead>
        <tbody>
            {''.join([f'<tr>{"".join([f"<td>{row[col]}</td>" for col in df.columns])}</tr>' for _, row in df.iterrows()])}
        </tbody>
    </table>

    <script>
        $(document).ready(function() {{
            $('#table1').DataTable({{
                "pageLength": 50
            }});
            $('#table2').DataTable({{
                "pageLength": 50
            }});
        }});
    </script>
</body>
</html>
"""

# Write HTML content to file with UTF-8 encoding
with open('dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Dashboard saved as 'dashboard.html'")
