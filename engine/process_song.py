import json                                                     
import sys                                                      
import os                                                       
                                                                
file_path = sys.argv[1]                                         
difficulty = sys.argv[2].lower()                                
title = os.path.basename(file_path)                             
                                                                
charts = {                                                      
"beginner": {                                                   
"confidence": 0.72,                                             
"sections": [                                                   
{"name": "Intro", "bars": ["HH x-x-x-x-\nSD ----o---\nBD o---o---"]},                                                      
{"name": "Verse", "bars": ["HH x-x-x-x-\nSD ----o---\nBD o-o---o-"]},                                                      
],                                                              
},                                                              
"intermediate": {                                               
"confidence": 0.78,                                             
"sections": [                                                   
{"name": "Intro", "bars": ["HH x-xx-x-x\nSD ----o---\nBD o---o-o-"]},                                                      
{"name": "Verse", "bars": ["HH x-xx-x-x\nSD ----o-g-\nBD o-o---o-"]},                                                      
],                                                              
},                                                              
"pro": {                                                        
"confidence": 0.84,                                             
"sections": [                                                   
{"name": "Intro", "bars": ["HH x-xx-x-x\nSD --g-o-g-\nBD o---o-o-"]},                                                      
{"name": "Verse", "bars": ["HH x-xx-xx-\nSD ----o-g-\nBD oo--o---"]},                                                      
{"name": "Fill", "bars": ["T1 ----oo--\nT2 --oo----\nFT oo------"]},                                                      
],                                                              
},                                                              
}                                                               
                                                                
data = charts.get(difficulty)                                   
if not data:                                                    
    print(json.dumps({"error": "Invalid difficulty"}))              
    sys.exit(1)                                                     
                                                                
print(json.dumps({                                              
"title": f"Demo chart for {title}",                             
"difficulty": difficulty,                                       
"confidence": data["confidence"],                               
"sections": data["sections"]                                    
}))    