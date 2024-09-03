from graphviz import Digraph

def create_doorphone_diagram(with_amplifier=False):
    dot = Digraph(comment='Doorphone System')
    dot.attr(rankdir='TB', size='12,8')

    # Create nodes
    dot.node('dp', 'Блок вызова\nELTIS DP', shape='box', style='filled', fillcolor='black', fontcolor='white')
    dot.node('ps', 'БП ELTIS\nPS2...', shape='box', style='filled', fillcolor='green', fontcolor='white')
    
    if with_amplifier:
        dot.node('amp', 'Усилитель\nELTIS UD-SA-1', shape='box', style='filled', fillcolor='blue', fontcolor='white')
    
    for i in range(2):
        dot.node(f'comm{i}', f'Коммутатор\nELTIS KMF-4.1\n(или KMF- 6.1)', shape='box', style='filled', fillcolor='blue', fontcolor='white')
        for j in range(4):
            dot.node(f'handset{i}{j}', 'Абонентская\nаудиотрубка', shape='box', style='filled', fillcolor='orange')

    # Create edges
    dot.edge('dp', 'ps', color='green')
    
    if with_amplifier:
        dot.edge('dp', 'amp', color='blue', label='3')
        dot.edge('amp', 'comm0', color='blue')
        dot.edge('amp', 'comm1', color='blue')
        dot.edge('ps', 'amp', color='green', label='2')
    else:
        dot.edge('dp', 'comm0', color='blue', label='3')
        dot.edge('dp', 'comm1', color='blue', label='3')

    for i in range(2):
        for j in range(4):
            dot.edge(f'comm{i}', f'handset{i}{j}', color='lightblue')

    return dot

# Generate both diagrams
diagram1 = create_doorphone_diagram(with_amplifier=False)
diagram2 = create_doorphone_diagram(with_amplifier=True)

# Save diagrams as PNG files
diagram1.render('doorphone_diagram1', format='png', cleanup=True)
diagram2.render('doorphone_diagram2', format='png', cleanup=True)




import os
from graphviz import Digraph

def create_doorphone_diagram(with_amplifier=False):
    dot = Digraph(comment='Doorphone System')
    dot.attr(rankdir='TB', size='12,8')

    # Create nodes
    dot.node('dp', 'Блок вызова\nELTIS DP', shape='box', style='filled', fillcolor='black', fontcolor='white')
    dot.node('ps', 'БП ELTIS\nPS2...', shape='box', style='filled', fillcolor='green', fontcolor='white')
    
    if with_amplifier:
        dot.node('amp', 'Усилитель\nELTIS UD-SA-1', shape='box', style='filled', fillcolor='blue', fontcolor='white')
    
    for i in range(2):
        dot.node(f'comm{i}', f'Коммутатор\nELTIS KMF-4.1\n(или KMF- 6.1)', shape='box', style='filled', fillcolor='blue', fontcolor='white')
        for j in range(4):
            dot.node(f'handset{i}{j}', 'Абонентская\nаудиотрубка', shape='box', style='filled', fillcolor='orange')

    # Create edges
    dot.edge('dp', 'ps', color='green')
    
    if with_amplifier:
        dot.edge('dp', 'amp', color='blue', label='3')
        dot.edge('amp', 'comm0', color='blue')
        dot.edge('amp', 'comm1', color='blue')
        dot.edge('ps', 'amp', color='green', label='2')
    else:
        dot.edge('dp', 'comm0', color='blue', label='3')
        dot.edge('dp', 'comm1', color='blue', label='3')

    for i in range(2):
        for j in range(4):
            dot.edge(f'comm{i}', f'handset{i}{j}', color='lightblue')

    return dot

def set_graphviz_path():
    # Update PATH environment variable for this session
    graphviz_path = r'C:\Users\134\anaconda3\pkgs\graphviz-11.0.0-h09e431a_0\Library\bin\dot.exe'  # Adjust this path
    os.environ['PATH'] = graphviz_path + os.pathsep + os.environ['PATH']

# Set the path to Graphviz executables
set_graphviz_path()

# Generate both diagrams
diagram1 = create_doorphone_diagram(with_amplifier=False)
diagram2 = create_doorphone_diagram(with_amplifier=True)

# Save diagrams as PNG files
diagram1.render('doorphone_diagram1', format='png', cleanup=True)
diagram2.render('doorphone_diagram2', format='png', cleanup=True)


############################################################################################
import graphviz




def generate_graphviz_image(dot_code, output_file):
    # Create a Graphviz object
    graph = graphviz.Source(dot_code)
    
    # Render the graph to a file
    graph.render(output_file, format='png', cleanup=True)
    print(f"Image saved as {output_file}.png")
    
    


# Function to process and save diagrams from DOT code
def process_dot_code(dot_code_response):
    # Extract individual Digraph parts from the response
    # Assuming each Digraph is separated by '}' or a specific delimiter
    # This is a basic example of splitting; adjust if necessary
    dot_parts = dot_code_response.strip().split('}')
    
    # Remove empty parts and add '}' to each part
    dot_parts = [part.strip() + '}' for part in dot_parts if part.strip()]

    # Generate and save images
    for i, dot_code in enumerate(dot_parts):
        output_file = f'diagram_{i + 1}'
        generate_graphviz_image(dot_code, output_file)
        
 
        
# Get the DOT code from Claude AI
dot_code_response = get_claude_response(text_to_send)

# Process and save diagrams
process_dot_code(dot_code_response)
        

# Paste the Graphviz code here
dot_code = """
digraph ELTISDoorphone {
    # ... (paste the entire Graphviz code here)
digraph ELTISDoorphone {
    rankdir=TB;
    node [shape=box, style=filled, color=lightblue];
    
    // Main components
    BlockVyzova [label="Блок вызова\nELTIS DP"];
    Kommutator [label="Коммутатор\nELTIS\nКМ100-7.х"];
    
    // Connection components
    Stoyak [label="Стояк:\nдесятки\nи единицы\n(10-20 жил)", shape=ellipse];
    KommDesyatki [label="Коммутация\nДесятки"];
    KommEdinitsy1 [label="Коммутация\nЕдиницы"];
    KommEdinitsy2 [label="Коммутация\nЕдиницы"];
    KommEdinitsy3 [label="Коммутация\nЕдиницы"];
    KommEdinitsy4 [label="Коммутация\nЕдиницы"];
    
    // Handsets
    Handset1 [label="Абонентская\nаудиотрубка"];
    Handset2 [label="Абонентская\nаудиотрубка"];
    Handset3 [label="Абонентская\nаудиотрубка"];
    Handset4 [label="Абонентская\nаудиотрубка"];
    
    // Connections
    BlockVyzova -> Kommutator;
    Kommutator -> Stoyak;
    Stoyak -> KommDesyatki;
    KommDesyatki -> {KommEdinitsy1 KommEdinitsy2 KommEdinitsy3 KommEdinitsy4};
    KommEdinitsy1 -> Handset1;
    KommEdinitsy2 -> Handset2;
    KommEdinitsy3 -> Handset3;
    KommEdinitsy4 -> Handset4;
    
    // Ranking
    {rank=same; KommEdinitsy1 KommEdinitsy2 KommEdinitsy3 KommEdinitsy4}
    {rank=same; Handset1 Handset2 Handset3 Handset4}
}


}
"""

# Generate the image
generate_graphviz_image(dot_code, 'eltis_doorphone_system')
