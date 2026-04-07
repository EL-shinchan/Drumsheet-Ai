export type Difficulty = "beginner" | "intermediate" | "pro";   
                                                                   
   export type DrumSection = {                                     
   name: string;                                                   
   bars: string[];                                                 
   };                                                              
                                                                   
   export type GenerationResult = {                                
   title: string;                                                  
   difficulty: Difficulty;                                         
   confidence: number;                                             
   sections: DrumSection[];                                        
   };                        