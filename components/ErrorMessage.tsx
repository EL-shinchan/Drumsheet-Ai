   type ErrorMessageProps = {                                      
   message: string | null;                                         
   };                                                              
                                                                   
   export default function ErrorMessage({ message }:               
 ErrorMessageProps) {                                              
   if (!message) return null;                                      
                                                                   
   return (                                                        
   <div className="rounded-2xl border border-red-900 bg-red-950/40 
 p-5 text-sm font-medium text-red-200">                            
   {message}                                                       
   </div>                                                          
   );                                                              
   }  