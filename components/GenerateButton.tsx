   type GenerateButtonProps = {                                    
   disabled?: boolean;                                             
   loading?: boolean;                                              
   onClick: () => void;                                            
   };                                                              
                                                                   
   export default function GenerateButton({                        
   disabled,                                                       
   loading,                                                        
   onClick,                                                        
   }: GenerateButtonProps) {                                       
   return (                                                        
   <div className="rounded-2xl border border-slate-800             
 bg-slate-900 p-5">                                                
   <button                                                         
   type="button"                                                   
   onClick={onClick}                                               
   disabled={disabled || loading}                                  
   className="w-full rounded-xl bg-gradient-to-r from-blue-600     
 to-violet-600 px-5 py-3 font-semibold text-white transition       
 hover:opacity-95 disabled:cursor-not-allowed disabled:opacity-50" 
   >                                                               
   {loading ? "Generating..." : "Generate Drum Sheet"}             
   </button>                                                       
   </div>                                                          
   );                                                              
   } 