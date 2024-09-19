import random
import pandas as pd

def generate_initial_stock(num_stages):
    return [random.randint(0, 100) for _ in range(num_stages)]

def calculate_replenishment(initial_stock, monthly_consumption):
    total_initial = sum(initial_stock)
    replenishment = max(0, monthly_consumption - total_initial)
    stages = len(initial_stock)
    
    df = pd.DataFrame(columns=[f'Этап {i+1}' for i in range(stages)])
    df.loc['Начальный'] = initial_stock
    df.loc['Пополнение'] = [replenishment] + [0] * (stages - 1)
    
    current_stock = initial_stock.copy()
    current_stock[0] += replenishment
    
    for i in range(stages - 1):
        move_amount = sum(current_stock[:i+1])
        row = [0] * stages
        row[i+1] = move_amount
        df.loc[f'Перемещение {i+1} в {i+2}'] = row
        current_stock = [0] * (i+1) + [sum(current_stock[:i+2])] + current_stock[i+2:]
    
    df.loc['Конечный'] = [0] * (stages - 1) + [monthly_consumption]
    
    return df

def generate_markdown(positions):
    markdown = "# Планы пополнения запасов для 10 позиций\n\n"
    
    for i, position in enumerate(positions, 1):
        markdown += f"## Позиция {i}\n\n"
        markdown += f"Количество этапов: {position['stages']}\n"
        markdown += f"Ежемесячное потребление: {position['consumption']} шт.\n\n"
        markdown += position['df'].to_markdown()
        markdown += "\n\n"
    
    return markdown

# Generate data for 10 positions
positions = []
for _ in range(10):
    stages = random.randint(2, 4)
    initial_stock = generate_initial_stock(stages)
    monthly_consumption = random.randint(sum(initial_stock), sum(initial_stock) + 300)
    
    df = calculate_replenishment(initial_stock, monthly_consumption)
    
    positions.append({
        'stages': stages,
        'consumption': monthly_consumption,
        'df': df
    })

# Generate markdown
markdown_output = generate_markdown(positions)

# Save to file
with open('stock_replenishment_plans.md', 'w', encoding='utf-8') as f:
    f.write(markdown_output)

print("Markdown file 'stock_replenishment_plans.md' has been generated.")