import re
from bs4 import BeautifulSoup
import pandas as pd
from datetime import date, datetime
import os



def parse_html_file(file_path):
    # Read the HTML file
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Create a BeautifulSoup object
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract all changedDate occurrences
    changed_dates = [span.text.strip() for span in soup.find_all('span', id='changedDate')]

    # Extract all CREATED_BY_label occurrences
    created_by_pattern = r'CREATED_BY_label&quot;:\[&quot;(.*?)&quot;'
    created_by_matches = re.findall(created_by_pattern, html_content)

    # Extract all RESPONSIBLE_ID_label occurrences
    responsible_id_pattern = r'RESPONSIBLE_ID_label&quot;:\[&quot;(.*?)&quot;'
    responsible_id_matches = re.findall(responsible_id_pattern, html_content)

    # Extract all task-status-text-color-completed occurrences
    completed_tasks = [a.get_text(strip=True).split('\n')[0] for a in soup.find_all('a', class_='task-title task-status-text-color-completed')]

    # Extract all task-status-text-color-in-progress occurrences
    in_progress_tasks = [a.get_text(strip=True).split('\n')[0] for a in soup.find_all('a', class_='task-title task-status-text-color-in-progress')]
    
    tasks_tag = [span.text.strip() for span in soup.find_all('span', class_='main-grid-tag-inner')] 

    # Extract all bxt-tasks-grid-deadline occurrences
    deadlines = [span.text.strip() for span in soup.find_all('span', class_='bxt-tasks-grid-deadline')]
    
    # Extract the numeric value after the hyphen in the id attribute of span with class task-timer
    task_timer_ids = [re.search(r'id="task-timer-block-container-(\d+)"', str(span)).group(1)
                   for span in soup.find_all('span', class_='task-timer')]

    return {
        'changedDate': changed_dates,
        'CREATED_BY_label': created_by_matches,
        'RESPONSIBLE_ID_label': responsible_id_matches,
        'completed_tasks': completed_tasks,
        'in_progress_tasks': in_progress_tasks,
        'tag':tasks_tag,
        'deadlines': deadlines,
        'task_timer_ids': task_timer_ids 
        
    }




# Usage
file_path = 'C:\\Users\\134\\Documents\\Мои задачи.html'
result = parse_html_file(file_path)
# Find the index of the element before which you want to insert

# if an element is missing and needs to be inserted
# index = result['in_progress_tasks'].index('Пожелания Татьяны Линниковой от 22.08.20243')

# # Insert the new element at the found index
# result['in_progress_tasks'].insert(index, 'Создание отчетов: контроль остатков плана отгрузки и материалов в работе')

df_in_progress = pd.DataFrame({
    "Задачи в работе": result['in_progress_tasks'],
    "Создано": result['CREATED_BY_label'],
    "Дата изменения": result['changedDate'],
    "Ответственный": result['RESPONSIBLE_ID_label'],
    "Крайний срок": result['deadlines'],
    "Номер задачи": result['task_timer_ids']
    
})

# Define the base URL
base_url = "https://gtconsulting.bitrix24.ru/company/personal/user/228/tasks/task/view/"

# Create the hyperlink column
df_in_progress['Ссылка на задачу'] = '=HYPERLINK("' + base_url + df_in_progress['Номер задачи'].astype(str) +"/" + '", "Открыть в Битрикс")'
df_in_progress['URL'] = base_url + df_in_progress['Номер задачи'].astype(str) +"/ " 


    # Conditionally add the 'Tag' column. Tags currently are not used
try:
    if len(result['tasks_tag']) == len(result['in_progress_tasks']):
        df_in_progress["Tag"] = result['tasks_tag']
except:
    pass        

formatted_date = date.today().strftime("%d_%m_%Y")

# Define the file path with the formatted date
file_path = fr"C:\Users\134\Documents\ЭЛТИС\Битрикс\задачи_в_работе_Битрикс_{formatted_date}.csv"
# Save the DataFrame to the specified CSV file
df_in_progress.to_csv(file_path, index=False, encoding='utf-8-sig')


# Define the file path with the formatted date. Save in Excel foramt
output_path = fr"C:\Users\134\Documents\ЭЛТИС\Битрикс\задачи_в_работе_Битрикс_{formatted_date}.xlsx"
df_in_progress.to_excel(output_path, index=False)



# # for completed tasks
file_path = 'C:\\Users\\134\\Documents\\Мои задачи_завершен.html'
result = parse_html_file(file_path)

df_completed = pd.DataFrame({
    "Завершенные задачи": result['completed_tasks'],
    "Создано": result['CREATED_BY_label'],
    "Дата изменения": result['changedDate'],
    "Ответственный": result['RESPONSIBLE_ID_label'],
    "Крайний срок": result['deadlines'],
    "Номер задачи": result['task_timer_ids']
})

# Create the hyperlink column
df_completed['Ссылка на задачу'] = '=HYPERLINK("' + base_url + df_completed['Номер задачи'].astype(str) +"/" + '", "Открыть в Битрикс")'
df_completed['URL'] = base_url + df_completed['Номер задачи'].astype(str) +"/ " 

# Define the file path with the formatted date
file_path = fr"C:\Users\134\Documents\ЭЛТИС\Битрикс\завершенные_задачи_Битрикс_{formatted_date}.csv"
# Save the DataFrame to the specified CSV file
df_completed.to_csv(file_path, index=False, encoding='utf-8-sig')


# Define the file path with the formatted date. Save in Excel foramt
output_path = fr"C:\Users\134\Documents\ЭЛТИС\Битрикс\завершенные_задачи_Битрикс_{formatted_date}.xlsx"
df_completed.to_excel(output_path, index=False)



####################################################
# compare tasks in progress to find if there is anything new

# Folder path
folder_path = r"C:\Users\134\Documents\ЭЛТИС\Битрикс"

# Pattern to match files with "задачи_в_работе_Битрикс" in the name and extract the date
pattern = re.compile(r'задачи_в_работе_Битрикс.*_(\d{2}_\d{2}_\d{4})\.xlsx')

# List to hold file names and their corresponding dates
files_with_dates = []

# Iterate over files in the directory
for file_name in os.listdir(folder_path):
    # Check if the file matches the pattern
    match = pattern.search(file_name)
    if match:
        # Extract date string from the file name
        date_str = match.group(1)
        # Convert date string to a datetime object
        date_obj = datetime.strptime(date_str, '%d_%m_%Y')
        # Append to the list as a tuple (date, file_name)
        files_with_dates.append((date_obj, file_name))

# Sort files by date (oldest first)
files_with_dates.sort(reverse=True)

# Filter out the two oldest files
oldest_files = files_with_dates[:2]


# the current version of tasks list from Bitrix
df1 = pd.read_excel(os.path.join(folder_path, oldest_files[0][1]))


# the previouse version of rasks list from Bitrix
df2 = pd.read_excel(os.path.join(folder_path, oldest_files[1][1]))

df1 ["Приоритет"] = df2["Приоритет"]

# Perform an anti-join to find records in df1 that are not in df2 based on the "Номер задачи" column
anti_join = df1.merge(df2, on='Номер задачи', how='left', indicator=True)
new_records = anti_join[anti_join['_merge'] == 'left_only'].drop(columns='_merge')

# Output the new records
print("New records in the first dataset compared to the second dataset (based on 'Номер задачи'):")
print(new_records)

output_path = fr"C:\Users\134\Documents\ЭЛТИС\Битрикс\новые_задачи_Битрикс_{formatted_date}.xlsx"
new_records.to_excel(output_path, index=False)


# Perform an anti-join to find records in df2 that are not in df1 based on the "Номер задачи" column
anti_join_reverse = df2.merge(df1, on='Номер задачи', how='left', indicator=True)
old_records = anti_join_reverse[anti_join_reverse['_merge'] == 'left_only'].drop(columns='_merge')

# Output the old records
print("Records that were in the second dataset but not in the first dataset (based on 'Номер задачи'):")
print(old_records)


output_path = fr"C:\Users\134\Documents\ЭЛТИС\Битрикс\завершенные_задачи_Битрикс_{formatted_date}.xlsx"
old_records.to_excel(output_path, index=False)




df2['Номер задачи'] = df2['Номер задачи'].fillna(0).astype(float).astype(int)


# Convert both 'Номер задачи' columns to strings
df2['Номер задачи'] = df2['Номер задачи'].astype(str)
df_in_progress['Номер задачи'] = df_in_progress['Номер задачи'].astype(str)

# Now merge the DataFrames
df_in_progress_with_sprint_data = df_in_progress.merge(
    df2[['Номер задачи', 'Отдел', 'Приоритет', 'Задача на период до 15 сент (спринт 1)']],
    on='Номер задачи',
    how='left',
    indicator=True
)




# Reorder columns according to the specified list
df_in_progress_with_sprint_data = df_in_progress_with_sprint_data[
    ['Номер задачи', 'Задачи в работе', 'Отдел', 'Приоритет', 'Задача на период до 15 сент (спринт 1)',
     'Создано', 'Дата изменения', 'Ответственный', 'Крайний срок', 'Ссылка на задачу', 'URL']
]



# Sort the DataFrame by 'Приоритет' and 'Задача на период до 15 сент (спринт 1)' in ascending order
df_in_progress_with_sprint_data = df_in_progress_with_sprint_data.sort_values(
    by=['Задача на период до 15 сент (спринт 1)', 'Приоритет' ], 
    ascending=[True, False]
)


output_path = fr"C:\Users\134\Documents\ЭЛТИС\Битрикс\задачи_в_работе_Битрикс_{formatted_date}.xlsx"
df_in_progress_with_sprint_data.to_excel(output_path, index=False)











###############################################
# get previous online meeting data
pattern = re.compile(rf'резюме.*_(\d{{2}}_\d{{2}}_\d{{4}})\.{"xlsx"}')

def get_files_with_dates(folder_path, pattern):
    # Pattern to match files with "задачи_в_работе_Битрикс" in the name and extract the date
    
    
    # List to hold file names and their corresponding dates
    files_with_dates = []

    # Iterate over files in the directory
    for file_name in os.listdir(folder_path):
        # Check if the file matches the pattern
        match = pattern.search(file_name)
        if match:
            # Extract date string from the file name
            date_str = match.group(1)
            # Convert date string to a datetime object
            date_obj = datetime.strptime(date_str, '%d_%m_%Y')
            # Append to the list as a tuple (date, file_name)
            files_with_dates.append((date_obj, file_name))

    # Sort files by date (newest first)
    files_with_dates.sort(reverse=True)
    
    return files_with_dates

online_meeting_files =get_files_with_dates (r"C:\Users\134\Documents\ЭЛТИС\Онлайн совещания", pattern)

# Sort files by date (oldest first)
online_meeting_files.sort(reverse=True)

prev_meeting_file_name = online_meeting_files [:1]

# load tasks from previous online meeting
df_prev_onine_meeting = pd.read_excel(r"C:\Users\134\Documents\ЭЛТИС\Онлайн совещания\резюме_29_08_2024.xlsx")

#################################################

