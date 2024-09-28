import anthropic
import os
import sys

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key=api_key,
)

def send_message(text_to_send):
    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=4096,
        messages=[
            {"role": "user", "content": text_to_send}
        ]
    )
    return message.content


def format_claude_reply(reply):
    # Extract the text from the TextBlock
    text = reply[0].text
    
    # Split the text into lines
    lines = text.split('\n')
    
    # Format each line
    formatted_lines = []
    for line in lines:
        # Remove leading/trailing whitespace
        line = line.strip()
        
        # Add appropriate indentation for list items
        if line.startswith('-'):
            line = '  ' + line
        elif line[0:2].isdigit() and line[2] == '.':
            line = line
        elif line.startswith('   -'):
            line = '    ' + line
        
        formatted_lines.append(line)
    
    # Join the formatted lines back together
    formatted_text = '\n'.join(formatted_lines)
    
    return formatted_text



if __name__ == "__main__":
    text_to_send_tech_support = sys.stdin.read().strip()
    claude_reply_tech_support = format_claude_reply(send_message(text_to_send_tech_support))
    print(claude_reply_tech_support)