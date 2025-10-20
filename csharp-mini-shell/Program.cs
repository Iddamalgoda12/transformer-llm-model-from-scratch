using System;

while (true)
{
    Console.Write("$ ");

    //checks the input for null also,removes spaces
    String? input = Console.ReadLine()?.Trim();

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
    
    //added type command to find out buitin comands
    if(command == "type")
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
}





