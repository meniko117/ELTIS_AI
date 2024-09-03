from bs4 import BeautifulSoup
import pandas as pd
import re

# Step 1: Read and parse the HTML file
with open('C:\\Users\\134\\Documents\\Мои задачи.html', 'r', encoding='utf-8') as file:
    soup = BeautifulSoup(file, 'html.parser')

# Step 2: Extract task information
tasks = []

# Define regex patterns to match CREATED_BY_label and RESPONSIBLE_ID_label
created_by_pattern = re.compile(r'CREATED_BY_label&quot;:\[&quot;(.*?)&quot;')
responsible_id_pattern = re.compile(r'RESPONSIBLE_ID_label&quot;:\[&quot;(.*?)&quot;')

selectors = {
    "title_completed": "task-title task-status-text-color-completed",
    "title_in_progress": "task-title task-status-text-color-in-progress"}

# Step 3: Loop through the relevant tags and extract the data
for title_completed, title_in_progress, deadline, changed_date, created_by, responsible_id in zip(
    soup.find_all(class_=selectors["title_completed"]),
    soup.find_all(class_=selectors["title_in_progress"]),
    soup.find_all('span', class_="bxt-tasks-grid-deadline"),
    soup.find_all('span', id="changedDate"),
    re.findall(created_by_pattern, soup.prettify()),  # Find all occurrences in the HTML
    re.findall(responsible_id_pattern, soup.prettify())  # Find all occurrences in the HTML
):
    # Create a dictionary for each task
    task = {
        "Title Completed": title_completed.get_text(strip=True),  # Extract text for completed tasks
        "Title In Progress": title_in_progress.get_text(strip=True),  # Extract text for in-progress tasks
        "Deadline": deadline.get_text(strip=True),  # Extract the deadline date
        "Changed Date": changed_date.get_text(strip=True),  # Extract the changed date
        "Created By": created_by,  # Extract the created by name
        "Responsible ID": responsible_id  # Extract the responsible ID name
    }
    # Add the dictionary to the list
    tasks.append(task)

# Step 4: Create a DataFrame from the list of task dictionaries
tasks_df = pd.DataFrame(tasks)

# Display or save the table
print(tasks_df)
tasks_df.to_csv('tasks_data.csv', index=False)  # Save to a CSV file if needed




