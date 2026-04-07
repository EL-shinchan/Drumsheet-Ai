 import { GenerationResult } from "@/lib/types";                 
                                                                   
   type DrumSheetPreviewProps = {                                  
   result: GenerationResult | null;                                
   };                                                              
                                                                   
   export default function DrumSheetPreview({ result }:            
 DrumSheetPreviewProps) {                                          
   if (!result) return null;                                       
                                                                   
   return (                                                        
   <div className="rounded-2xl border border-slate-800             
 bg-slate-900 p-5">                                                
   <div className="mb-5">                                          
   <h2 className="text-2xl font-bold                               
 text-slate-100">{result.title}</h2>                               
   <p className="mt-2 text-sm text-slate-300">                     
   Difficulty: <strong>{result.difficulty}</strong> ·              
 Confidence:{" "}                                                  
   <strong>{Math.round(result.confidence * 100)}%</strong>       
   </p>                                                            
   </div>                                                          
                                                                   
   <div className="space-y-5">                                     
   {result.sections.map((section) => (                             
   <div                                                            
   key={section.name}                                              
   className="border-t border-slate-800 pt-5 first:border-t-0      
 first:pt-0"                                                       
   >                                                               
   <h3 className="mb-3 text-lg font-semibold text-slate-100">      
   {section.name}                                                  
   </h3>                                                           
                                                                   
   <div className="space-y-3">                                     
   {section.bars.map((bar, index) => (                             
   <pre                                                            
   key={`${section.name}-${index}`}                                
   className="overflow-x-auto rounded-xl border border-slate-800   
 bg-slate-950 p-4 text-sm text-slate-200"                          
   >                                                               
   {bar}                                                           
   </pre>                                                          
   ))}                                                             
   </div>                                                          
   </div>                                                          
   ))}                                                             
   </div>                                                          
   </div>                                                          
   );                                                              
   }                  