using System;
using System.Diagnostics;

while (true)
{
    Console.Write("$ ");

    //checks the input for null also,removes spaces
    String? input = Console.ReadLine()?.Trim();
    
    //skips if command is null
    if (string.IsNullOrEmpty(input))
    {
        continue;
    }

    //devids input in to parts
    string[] parts = input.Split(' ', StringSplitOptions.RemoveEmptyEntries);
    string command = parts[0].ToLower();

    //exit codes added
    if (command == "exit")
    {
        int exitcode = 0;
        if (parts.Length > 1 && int.TryParse(parts[1], out int code))
        {
            exitcode = code;
        }
        Environment.Exit(exitcode);

    }
    
    //echo command
    if(command == "echo")
    {
        if(parts.Length>1)
        {
           Console.WriteLine(string.Join(' ', parts[1..]));
        }
        continue;

    }
    //pwd command
    if (command == "pwd")
    {
        Console.WriteLine(Environment.CurrentDirectory);
        continue;
    }

    //added type command to find out buitin comands
    if (command == "type")
    {
        if (parts.Length > 1)
        {
            if (parts[1] == "echo" || parts[1] == "exit" || parts[1] == "type")
            {
                Console.WriteLine($"{parts[1]}: is a shell builtin");
            }
            
            else
            {
                string? pathvar = Environment.GetEnvironmentVariable("PATH");
                if(pathvar!=null)
                {
                    bool found = false;
                    string[] paths = pathvar.Split(';');
                    foreach(string dir in paths)
                    {
                        string fullpath = Path.Combine(dir, parts[1]);
    //prints the full path of the file.
                        if(File.Exists(fullpath))
                        {
                            Console.WriteLine($"{parts[1]} is {fullpath}");
                            found = true;
                            break;
                        }

                    }
                    if(!found)
                    {
                        Console.WriteLine($"{parts[1]} not found");
                    }
                }
            }

        }
            continue;
    }
    //try command. runs files that are on my pc.
    try
    {
        string? pathvar = Environment.GetEnvironmentVariable("PATH");
        string[] paths = pathvar?.Split(";") ?? Array.Empty<string>();
        string[] exts = { " ", ".exe", ".bat", ".cmd" };
        string? fullpath = null;

        foreach(string dir in paths)
        {
            foreach(var ext in exts)
            {
                string possiblepath = Path.Combine(dir, parts[0] + ext);
                if(File.Exists(possiblepath))
                {
                    fullpath = possiblepath;
                    break;
                }

            }
            if (fullpath != null) break;

        }
        if(fullpath==null)
        {
            Console.WriteLine($"{parts[0]}:command not found");
            continue;
        }

        ProcessStartInfo psi = new ProcessStartInfo
        {
            FileName = fullpath,
            Arguments = string.Join(' ', parts[1..]),
            UseShellExecute = false,
            RedirectStandardOutput = true,
            RedirectStandardError = true
        };

        Process proc = Process.Start(psi)!;
        string output = proc.StandardOutput.ReadToEnd();
        string error = proc.StandardError.ReadToEnd();
        proc.WaitForExit();

        if (!string.IsNullOrEmpty(output))
            Console.Write(output);
        if (!string.IsNullOrEmpty(error))
            Console.Write(error);

    }
    catch (Exception ex)
    {
        Console.WriteLine($"Error: {ex.Message}");
    }

}





