import re
from bs4 import BeautifulSoup
import pandas as pd
from datetime import date



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

