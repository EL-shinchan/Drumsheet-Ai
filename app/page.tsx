"use client";                                                   
                                                                   
   import { useState } from "react";                               
   import UploadBox from "@/components/UploadBox";                 
   import DifficultySelector from                                  
 "@/components/DifficultySelector";                                
   import GenerateButton from "@/components/GenerateButton";       
   import ProcessingStatus from "@/components/ProcessingStatus";   
   import DrumSheetPreview from "@/components/DrumSheetPreview";   
   import ErrorMessage from "@/components/ErrorMessage";           
   import { Difficulty, GenerationResult } from "@/lib/types";     
                                                                   
   export default function HomePage() {                            
   const [file, setFile] = useState<File | null>(null);            
   const [difficulty, setDifficulty] = useState<Difficulty |       
 null>(null);                                                      
   const [loading, setLoading] = useState(false);                  
   const [status, setStatus] = useState<string | null>(null);      
   const [error, setError] = useState<string | null>(null);        
   const [result, setResult] = useState<GenerationResult |         
 null>(null);                                                      
                                                                   
   async function handleGenerate() {                               
   if (!file) {                                                    
   setError("Please upload an audio file first.");                 
   return;                                                         
   }                                                               
                                                                   
   if (!difficulty) {                                              
   setError("Please choose a difficulty level.");                  
   return;                                                         
   }                                                               
                                                                   
   setLoading(true);                                               
   setError(null);                                                 
   setResult(null);                                                
   setStatus("Uploading file and preparing generation...");        
                                                                   
   try {                                                           
   const formData = new FormData();                                
   formData.append("audio", file);                                 
   formData.append("difficulty", difficulty);                      
                                                                   
   const response = await fetch("/api/generate", {                 
   method: "POST",                                                 
   body: formData,                                                 
   });                                                             
                                                                   
   setStatus("Processing song and building drum chart...");        
                                                                   
   if (!response.ok) {                                             
   const errorBody = await response.json().catch(() => null);      
   throw new Error(errorBody?.error || "Generation failed.");      
   }                                                               
                                                                   
   const data: GenerationResult = await response.json();           
   setResult(data);                                                
   setStatus("Done.");                                             
   } catch (err) {                                                 
   const message =                                                 
   err instanceof Error ? err.message : "Something went wrong.";   
   setError(message);                                              
   setStatus(null);                                                
   } finally {                                                     
   setLoading(false);                                              
   }                                                               
   }                                                               
                                                                   
   return (                                                        
   <main className="min-h-screen bg-slate-950 text-slate-100">     
   <div className="mx-auto max-w-4xl px-6 py-12">                  
   <section className="mb-8">                                      
   <h1 className="text-4xl font-bold tracking-tight">              
   AI Drum Sheet Generator                                         
   </h1>                                                           
   <p className="mt-3 text-lg text-slate-300">                     
   Upload a song and generate a playable drum chart.               
   </p>                                                            
   </section>                                                      
                                                                   
   <div className="space-y-5">                                     
   <UploadBox onFileChange={setFile} />                            
   <DifficultySelector value={difficulty} onChange={setDifficulty} 
  />                                                               
   <GenerateButton                                                 
   onClick={handleGenerate}                                        
   loading={loading}                                               
   disabled={!file || !difficulty}                                 
   />                                                              
   <ProcessingStatus message={status} />                           
   <ErrorMessage message={error} />                                
   <DrumSheetPreview result={result} />                            
   </div>                                                          
   </div>                                                          
   </main>                                                         
   );                                                              
   }                        