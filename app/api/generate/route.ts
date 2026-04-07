import { NextRequest, NextResponse } from "next/server";        
   import path from "path";                                        
   import fs from "fs/promises";                                   
   import { spawn } from "child_process";                          
                                                                   
   export const runtime = "nodejs";                                
                                                                   
   function runPythonScript(filePath: string, difficulty: string): 
 Promise<string> {                                                 
   return new Promise((resolve, reject) => {                       
   const scriptPath = path.join(process.cwd(), "engine",           
 "process_song.py");                                               
   const child = spawn("python3", [scriptPath, filePath,           
 difficulty]);                                                     
                                                                   
   let stdout = "";                                                
   let stderr = "";                                                
                                                                   
   child.stdout.on("data", (data) => {                             
   stdout += data.toString();                                      
   });                                                             
                                                                   
   child.stderr.on("data", (data) => {                             
   stderr += data.toString();                                      
   });                                                             
                                                                   
   child.on("close", (code) => {                                   
   if (code !== 0) {                                               
   reject(new Error(stderr || `Python process exited with code     
 ${code}`));                                                       
   return;                                                         
   }                                                               
                                                                   
   resolve(stdout);                                                
   });                                                             
   });                                                             
   }                                                               
                                                                   
   export async function POST(request: NextRequest) {              
   try {                                                           
   const formData = await request.formData();                      
   const file = formData.get("audio") as File | null;              
   const difficulty = formData.get("difficulty") as string | null; 
                                                                   
   if (!file) {                                                    
   return NextResponse.json(                                       
   { error: "No audio file uploaded." },                           
   { status: 400 }                                                 
   );                                                              
   }                                                               
                                                                   
   if (!difficulty) {                                              
   return NextResponse.json(                                       
   { error: "No difficulty selected." },                           
   { status: 400 }                                                 
   );                                                              
   }                                                               
                                                                   
   const bytes = await file.arrayBuffer();                         
   const buffer = Buffer.from(bytes);                              
                                                                   
   const uploadsDir = path.join(process.cwd(), "uploads");         
   await fs.mkdir(uploadsDir, { recursive: true });                
                                                                   
   const safeFilename = `${Date.now()}-${file.name.replace(/\s+/g, 
 "-")}`;                                                           
   const savedPath = path.join(uploadsDir, safeFilename);          
                                                                   
   await fs.writeFile(savedPath, buffer);                          
                                                                   
   const output = await runPythonScript(savedPath, difficulty);    
   const parsed = JSON.parse(output);                              
                                                                   
   return NextResponse.json(parsed);                               
   } catch (error) {                                               
   const message =                                                 
   error instanceof Error ? error.message : "Unexpected server error.";  
                                                                                                  
   return NextResponse.json({ error: message }, { status: 500 });  
   }                                                               
   }          