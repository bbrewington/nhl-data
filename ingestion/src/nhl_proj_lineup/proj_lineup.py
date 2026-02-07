import re

def parse_lineup_advanced(soup):
    header = soup.find('h3', string=lambda text: text and 'PROJECTED LINEUP' in text)
    
    if not header:
        return None
    
    # Get raw text content
    content_elements = []
    current = header.find_next_sibling()
    
    while current and current.name != 'h3':
        if current.name:
            content_elements.append(current.get_text())
        current = current.find_next_sibling()
    
    full_text = '\n'.join(content_elements)
    
    # Define position patterns
    position_pattern = r'^(Forwards?|Defensemen?|Defense|Goalies?)\s*$'
    player_line_pattern = r'^([^-\n]+(?:\s*-\s*[^-\n]+)*)\s*$'
    
    lineup = {}
    current_position = None
    
    for line in full_text.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        # Check for position header
        position_match = re.match(position_pattern, line, re.IGNORECASE)
        if position_match:
            current_position = position_match.group(1)
            lineup[current_position] = []
            continue
        
        # Check for player line
        if current_position and re.match(player_line_pattern, line):
            players = [p.strip() for p in line.split(' - ') if p.strip()]
            if players:
                lineup[current_position].append(players)
    
    return lineup

def parse_lineup_simple(soup):
    header = soup.find('h3', string=lambda text: text and 'PROJECTED LINEUP' in text)
    
    if not header:
        return None
    
    # Get all text as one block
    text_content = ""
    current = header.find_next_sibling()
    
    while current and current.name != 'h3':
        if current.name:
            text_content += current.get_text() + "\n"
        current = current.find_next_sibling()
    
    lines = [line.strip() for line in text_content.split('\n') if line.strip()]
    
    # Simple parsing
    positions = ['Forwards', 'Defensemen', 'Defense', 'Goalie', 'Goalies']
    lineup = {}
    current_pos = None
    
    for line in lines:
        if any(pos.lower() in line.lower() for pos in positions):
            current_pos = line
            lineup[current_pos] = []
        elif current_pos and ' - ' in line:
            players = [p.strip() for p in line.split(' - ')]
            lineup[current_pos].append(players)
        elif current_pos and line:  # Single player (like goalie)
            lineup[current_pos].append([line])
    
    return lineup

# Pretty print function
def print_lineup(lineup):
    for position, player_groups in lineup.items():
        print(f"\n{position}:")
        for i, group in enumerate(player_groups, 1):
            if len(group) == 3:  # Forward line
                print(f"  Line {i}: {' - '.join(group)}")
            elif len(group) == 2:  # Defense pair
                print(f"  Pair {i}: {' - '.join(group)}")
            else:  # Single player
                print(f"  {group[0]}")
                
def lineup_parser(soup):
    try:
        result = parse_lineup_advanced(soup)  # Option 2
        if validate_lineup(result):
            return result
    except Exception as e:
        log_error(f"Advanced parser failed: {e}")
    
    try:
        result = parse_lineup_simple(soup)  # Option 3 fallback
        return result
    except Exception as e:
        log_error(f"Simple parser failed: {e}")
        return None

def validate_lineup(lineup):
    """Check if parsed lineup makes sense"""
    if not lineup:
        return False
    
    # Check for reasonable number of players
    forwards = lineup.get('Forwards', [])
    if len(forwards) < 3 or len(forwards) > 6:  # Unusual number of forward lines
        return False
    
    # Check forward line sizes
    for line in forwards:
        if len(line) != 3:  # Forward lines should have 3 players
            return False
    
    return True